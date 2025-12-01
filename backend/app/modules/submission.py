"""
Module 1: File Submission, Retrieval, and Validation

Implements SRS requirements:
- M1.UC01: Submit File for Analysis (Upload / API Submit)
- M1.UC02: Handle Permission Error & Guide User

Handles:
1. File submission via upload or Google Drive link
2. Validation of file type, link format, and access permissions
3. Retrieval of Google Docs/DOCX files via Google Drive API
4. Temporary secure storage of retrieved files
5. Enqueueing validated files for metadata and content analysis
"""

import os
import hashlib
import mimetypes
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import magic
import uuid

from app import db
from app.models import Submission, SubmissionStatus, AuditLog
from app.services.validation_service import ValidationService
from app.services.audit_service import AuditService
from app.utils.file_utils import FileUtils

submission_bp = Blueprint('submission', __name__)

class SubmissionService:
    """Service class for handling file submissions and Google Drive integration"""
    
    def __init__(self):
        self.allowed_extensions = {'docx', 'doc'}
        self.allowed_mime_types = {
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'application/vnd.google-apps.document'
        }
    
    @property
    def max_file_size(self):
        """Get max file size from config (lazy load)"""
        return current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
        
    def _get_drive_service(self):
        """Initialize Google Drive API service"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                current_app.config['GOOGLE_SERVICE_ACCOUNT_FILE'],
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Google Drive service: {e}")
            raise Exception("Google Drive service unavailable")
    
    def validate_file(self, file):
        """Validate uploaded file according to SRS requirements"""
        errors = []
        
        # Check file size
        if len(file.read()) > self.max_file_size:
            errors.append(f"File size exceeds maximum limit of {self.max_file_size // (1024*1024)}MB")
        
        # Reset file pointer
        file.seek(0)
        
        # Check file extension
        filename = secure_filename(file.filename)
        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in self.allowed_extensions:
            errors.append("Unsupported file type. Only DOCX and DOC files are allowed.")
        
        # Check MIME type using python-magic for accuracy
        file_content = file.read(1024)  # Read first 1KB for MIME detection
        file.seek(0)  # Reset pointer
        
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            if mime_type not in self.allowed_mime_types:
                errors.append(f"Invalid file format. Detected: {mime_type}")
        except Exception as e:
            current_app.logger.warning(f"MIME type detection failed: {e}")
            # Fallback to filename-based validation
        
        return errors
    
    def validate_drive_link(self, drive_link):
        """Validate Google Drive link format and extract file ID"""
        import re
        
        # Google Drive link patterns
        patterns = [
            r'https://drive\.google\.com/file/d/([a-zA-Z0-9-_]+)',
            r'https://docs\.google\.com/document/d/([a-zA-Z0-9-_]+)',
            r'https://drive\.google\.com/open\?id=([a-zA-Z0-9-_]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, drive_link)
            if match:
                return match.group(1), None
        
        return None, "Invalid Google Drive link format"
    
    def get_drive_file_metadata(self, file_id):
        """Get file metadata from Google Drive"""
        try:
            service = self._get_drive_service()
            
            # Get file metadata
            metadata = service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,size,createdTime,modifiedTime,owners,lastModifyingUser'
            ).execute()
            
            return metadata, None
            
        except HttpError as e:
            error_details = e.error_details[0] if e.error_details else {}
            
            if e.resp.status == 403:
                if 'insufficientPermissions' in str(e) or 'permissionDenied' in str(e):
                    return None, {
                        'error_type': 'permission_denied',
                        'message': 'Insufficient permissions to access the file',
                        'guidance': self._get_permission_guidance()
                    }
            elif e.resp.status == 404:
                return None, {
                    'error_type': 'file_not_found',
                    'message': 'File not found or not accessible'
                }
            
            current_app.logger.error(f"Google Drive API error: {e}")
            return None, {
                'error_type': 'api_error',
                'message': 'Failed to access Google Drive'
            }
        
        except Exception as e:
            current_app.logger.error(f"Unexpected error accessing Drive file: {e}")
            return None, {
                'error_type': 'unknown_error',
                'message': 'Unexpected error occurred'
            }
    
    def download_drive_file(self, file_id, filename):
        """Download file from Google Drive to temporary storage"""
        try:
            service = self._get_drive_service()
            
            # For Google Docs, export as DOCX
            if filename.endswith('.gdoc') or 'google-apps.document' in str(filename):
                request_obj = service.files().export_media(
                    fileId=file_id,
                    mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                filename = filename.replace('.gdoc', '.docx')
            else:
                # For regular files, download as-is
                request_obj = service.files().get_media(fileId=file_id)
            
            # Execute download
            file_content = request_obj.execute()
            
            # Save to temporary storage
            temp_path = os.path.join(current_app.config['TEMP_STORAGE_PATH'], filename)
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            return temp_path, None
            
        except HttpError as e:
            current_app.logger.error(f"Failed to download Drive file: {e}")
            return None, f"Failed to download file: {e}"
        
        except Exception as e:
            current_app.logger.error(f"Unexpected error downloading file: {e}")
            return None, f"Unexpected error: {e}"
    
    def _get_permission_guidance(self):
        """Return guidance for fixing Google Drive permissions"""
        return {
            'steps': [
                "1. Open your Google Drive file",
                "2. Click the 'Share' button (top-right corner)",
                "3. Change access to 'Anyone with the link'",
                "4. Set permissions to 'Viewer' or 'Commenter'",
                "5. Copy the new link and resubmit"
            ],
            'help_url': '/help/drive-permissions'
        }
    
    def calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of file for integrity checking"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def create_submission_record(self, **kwargs):
        """Create submission record in database"""
        submission = Submission(
            job_id=str(uuid.uuid4()),
            **kwargs
        )
        
        try:
            db.session.add(submission)
            db.session.commit()
            
            # Log submission event
            AuditService.log_event(
                event_type='submission_created',
                description=f'New submission created: {submission.job_id}',
                submission_id=submission.id,
                metadata={'filename': submission.original_filename}
            )
            
            return submission, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create submission record: {e}")
            return None, str(e)

# Initialize service
submission_service = SubmissionService()

def validate_submission_token(token):
    """Validate submission token and return token with deadline info"""
    from app.models import SubmissionToken, Deadline
    from datetime import datetime
    
    if not token:
        return None, "No submission token provided"
    
    token_record = SubmissionToken.query.filter_by(token=token).first()
    
    if not token_record:
        return None, "Invalid submission token"
    
    if not token_record.is_valid():
        return None, "Submission token has expired or reached usage limit"
    
    # Check if token has an associated deadline (safely check if column exists)
    deadline_id = getattr(token_record, 'deadline_id', None)
    if deadline_id:
        deadline = Deadline.query.filter_by(id=deadline_id).first()
        if deadline:
            token_record.deadline_title = deadline.title
            token_record.deadline_datetime = deadline.deadline_datetime
    
    # Increment usage count
    token_record.usage_count += 1
    db.session.commit()
    
    return token_record, None

@submission_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload submissions
        
    SRS Reference: M1.UC01 - Submit File for Analysis (Upload)
    """
    try:
        # Get submission token (REQUIRED - links submission to professor)
        token = request.form.get('token') or request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Submission token is required. Please use the link provided by your professor.'}), 403
        
        token_record, error = validate_submission_token(token)
        if error:
            return jsonify({'error': error}), 403
        
        professor_id = token_record.professor_id
        # Use deadline from token (if column exists)
        deadline_id = getattr(token_record, 'deadline_id', None)
        
        # Validate request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Extract additional form data
        student_name = request.form.get('student_name', '').strip()
        student_email = request.form.get('student_email', '').strip()
        
        # Validate file
        validation_errors = submission_service.validate_file(file)
        if validation_errors:
            return jsonify({'error': '; '.join(validation_errors)}), 415
        
        # Secure filename and create paths
        original_filename = file.filename
        secure_name = secure_filename(original_filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{secure_name}"
        
        # Save file to temporary storage
        temp_path = os.path.join(current_app.config['TEMP_STORAGE_PATH'], unique_filename)
        file.save(temp_path)
        
        # Pre-validate the document before creating submission
        try:
            from app.modules.metadata import metadata_service
            
            # Try to extract metadata to validate document
            test_metadata, test_error = metadata_service.extract_docx_metadata(temp_path)
            if test_error:
                os.remove(temp_path)
                return jsonify({'error': f'Invalid document: {test_error}'}), 415
            
            # Try to extract text to ensure document is readable
            test_text, text_error = metadata_service.extract_document_text(temp_path)
            if text_error:
                os.remove(temp_path)
                return jsonify({'error': f'Cannot read document: {text_error}'}), 415
            
            # Check if document has content
            if not test_text or len(test_text.strip()) < 10:
                os.remove(temp_path)
                return jsonify({'error': 'Document appears to be empty or has insufficient content'}), 415
                
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'error': f'Invalid or corrupted document: {str(e)}'}), 415
        
        # Calculate file hash and size
        file_hash = submission_service.calculate_file_hash(temp_path)
        file_size = os.path.getsize(temp_path)
        mime_type = mimetypes.guess_type(temp_path)[0] or 'application/octet-stream'
        
        # Create folder based on deadline title
        if deadline_id:
            from app.models import Deadline
            deadline = Deadline.query.filter_by(id=deadline_id).first()
            if deadline:
                # Sanitize deadline title for folder name
                import re
                folder_name = re.sub(r'[<>:"/\\|?*]', '_', deadline.title)  # Remove invalid chars
                folder_name = folder_name.strip()[:100]  # Limit length
                deadline_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)
                
                # Create folder if it doesn't exist
                os.makedirs(deadline_folder, exist_ok=True)
                
                storage_path = os.path.join(deadline_folder, unique_filename)
            else:
                storage_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        else:
            # No deadline - use root upload folder
            storage_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        os.rename(temp_path, storage_path)
        
        # Create submission record
        submission, error = submission_service.create_submission_record(
            file_name=unique_filename,
            original_filename=original_filename,
            file_path=storage_path,
            file_size=file_size,
            file_hash=file_hash,
            mime_type=mime_type,
            submission_type='upload',
            student_name=student_name if student_name else None,
            student_email=student_email if student_email else None,
            deadline_id=deadline_id if deadline_id else None,
            professor_id=professor_id,
            status=SubmissionStatus.PENDING
        )
        
        if error:
            # Clean up file on database error
            try:
                os.remove(storage_path)
            except:
                pass
            return jsonify({'error': error}), 500
        
        # Trigger automatic analysis
        try:
            from app.modules.metadata import metadata_service
            
            # Update status to processing
            submission.status = SubmissionStatus.PROCESSING
            submission.processing_started_at = datetime.utcnow()
            db.session.commit()
            
            # Extract metadata
            metadata, metadata_error = metadata_service.extract_docx_metadata(storage_path)
            if not metadata_error:
                # Extract text
                text, text_error = metadata_service.extract_document_text(storage_path)
                if not text_error:
                    # Compute statistics
                    content_stats = metadata_service.compute_content_statistics(text)
                    is_complete, warnings = metadata_service.validate_document_completeness(content_stats, text)
                    
                    # Create or update analysis result
                    from app.models import AnalysisResult
                    analysis = AnalysisResult.query.filter_by(submission_id=submission.id).first()
                    if not analysis:
                        analysis = AnalysisResult(submission_id=submission.id)
                        db.session.add(analysis)
                    
                    analysis.document_metadata = metadata
                    analysis.content_statistics = content_stats
                    analysis.document_text = text
                    analysis.is_complete_document = is_complete
                    analysis.validation_warnings = warnings
                    
                    # Mark as completed
                    submission.status = SubmissionStatus.COMPLETED
                    submission.processing_completed_at = datetime.utcnow()
                    db.session.commit()
                    
                    current_app.logger.info(f"Analysis completed for submission {submission.id}")
        except Exception as e:
            current_app.logger.error(f"Auto-analysis failed: {e}")
            # Don't fail the upload, just log the error
            submission.status = SubmissionStatus.PENDING
            db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'job_id': submission.job_id,
            'submission_id': submission.id,
            'status': submission.status.value,
            'file_info': {
                'filename': original_filename,
                'size': file_size,
                'type': mime_type
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"File upload error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@submission_bp.route('/drive-link', methods=['POST'])
def submit_drive_link():
    """
    Handle Google Drive link submissions
    
    SRS Reference: M1.UC01 - Submit File for Analysis (Drive Link)
    """
    try:
        data = request.get_json()
        
        if not data or 'drive_link' not in data:
            return jsonify({'error': 'Google Drive link is required'}), 400
        
        # Get submission token (REQUIRED - links submission to professor)
        token = data.get('token') or request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Submission token is required. Please use the link provided by your professor.'}), 403
        
        token_record, error = validate_submission_token(token)
        if error:
            return jsonify({'error': error}), 403
        
        professor_id = token_record.professor_id
        # Use deadline from token (if column exists)
        deadline_id = getattr(token_record, 'deadline_id', None)
        
        drive_link = data['drive_link'].strip()
        student_name = data.get('student_name', '').strip()
        student_email = data.get('student_email', '').strip()
        
        # Validate drive link format
        file_id, validation_error = submission_service.validate_drive_link(drive_link)
        if validation_error:
            return jsonify({'error': validation_error}), 400
        
        # Get file metadata from Google Drive
        metadata, error = submission_service.get_drive_file_metadata(file_id)
        
        if error:
            if error['error_type'] == 'permission_denied':
                # Return permission guidance per SRS M1.UC02
                return jsonify({
                    'error': error['message'],
                    'error_type': 'permission_denied',
                    'guidance': error['guidance']
                }), 403
            else:
                return jsonify({'error': error['message']}), 400
        
        # Validate file type from metadata
        if metadata['mimeType'] not in submission_service.allowed_mime_types:
            return jsonify({
                'error': f"Unsupported file type: {metadata['mimeType']}"
            }), 415
        
        # Download file
        filename = f"{metadata['name']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        if not filename.endswith(('.docx', '.doc')):
            filename += '.docx'
        
        file_path, download_error = submission_service.download_drive_file(file_id, filename)
        
        if download_error:
            return jsonify({'error': download_error}), 500
        
        # Pre-validate the document before creating submission
        try:
            from app.modules.metadata import metadata_service
            
            # Try to extract metadata to validate document
            test_metadata, test_error = metadata_service.extract_docx_metadata(file_path)
            if test_error:
                os.remove(file_path)
                return jsonify({'error': f'Invalid document: {test_error}'}), 415
            
            # Try to extract text to ensure document is readable
            test_text, text_error = metadata_service.extract_document_text(file_path)
            if text_error:
                os.remove(file_path)
                return jsonify({'error': f'Cannot read document: {text_error}'}), 415
            
            # Check if document has content
            if not test_text or len(test_text.strip()) < 10:
                os.remove(file_path)
                return jsonify({'error': 'Document appears to be empty or has insufficient content'}), 415
                
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': f'Invalid or corrupted document: {str(e)}'}), 415
        
        # Calculate file hash
        file_hash = submission_service.calculate_file_hash(file_path)
        file_size = int(metadata.get('size', os.path.getsize(file_path)))
        
        # Create folder based on deadline title
        if deadline_id:
            from app.models import Deadline
            deadline = Deadline.query.filter_by(id=deadline_id).first()
            if deadline:
                # Sanitize deadline title for folder name
                import re
                folder_name = re.sub(r'[<>:"/\\|?*]', '_', deadline.title)  # Remove invalid chars
                folder_name = folder_name.strip()[:100]  # Limit length
                deadline_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)
                
                # Create folder if it doesn't exist
                os.makedirs(deadline_folder, exist_ok=True)
                
                storage_path = os.path.join(deadline_folder, filename)
            else:
                storage_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        else:
            # No deadline - use root upload folder
            storage_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        os.rename(file_path, storage_path)
        
        # Create submission record
        submission, error = submission_service.create_submission_record(
            file_name=filename,
            original_filename=metadata['name'],
            file_path=storage_path,
            file_size=file_size,
            file_hash=file_hash,
            mime_type=metadata['mimeType'],
            submission_type='drive_link',
            google_drive_link=drive_link,
            student_name=student_name if student_name else None,
            student_email=student_email if student_email else None,
            deadline_id=deadline_id if deadline_id else None,
            professor_id=professor_id,
            status=SubmissionStatus.PENDING
        )
        
        if error:
            # Clean up file on database error
            try:
                os.remove(storage_path)
            except:
                pass
            return jsonify({'error': error}), 500
        
        # Trigger automatic analysis
        try:
            from app.modules.metadata import metadata_service
            
            # Update status to processing
            submission.status = SubmissionStatus.PROCESSING
            submission.processing_started_at = datetime.utcnow()
            db.session.commit()
            
            # Extract metadata
            doc_metadata, metadata_error = metadata_service.extract_docx_metadata(storage_path)
            if not metadata_error:
                # Extract text
                text, text_error = metadata_service.extract_document_text(storage_path)
                if not text_error:
                    # Compute statistics
                    content_stats = metadata_service.compute_content_statistics(text)
                    is_complete, warnings = metadata_service.validate_document_completeness(content_stats, text)
                    
                    # Create or update analysis result
                    from app.models import AnalysisResult
                    analysis = AnalysisResult.query.filter_by(submission_id=submission.id).first()
                    if not analysis:
                        analysis = AnalysisResult(submission_id=submission.id)
                        db.session.add(analysis)
                    
                    analysis.document_metadata = doc_metadata
                    analysis.content_statistics = content_stats
                    analysis.document_text = text
                    analysis.is_complete_document = is_complete
                    analysis.validation_warnings = warnings
                    
                    # Mark as completed
                    submission.status = SubmissionStatus.COMPLETED
                    submission.processing_completed_at = datetime.utcnow()
                    db.session.commit()
                    
                    current_app.logger.info(f"Analysis completed for submission {submission.id}")
        except Exception as e:
            current_app.logger.error(f"Auto-analysis failed: {e}")
            # Don't fail the upload, just log the error
            submission.status = SubmissionStatus.PENDING
            db.session.commit()
        
        return jsonify({
            'message': 'Google Drive file retrieved successfully',
            'job_id': submission.job_id,
            'submission_id': submission.id,
            'status': submission.status.value,
            'file_info': {
                'filename': metadata['name'],
                'size': file_size,
                'type': metadata['mimeType'],
                'created_time': metadata.get('createdTime'),
                'modified_time': metadata.get('modifiedTime')
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Drive link submission error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@submission_bp.route('/status/<job_id>', methods=['GET'])
def get_submission_status(job_id):
    """Get submission status by job ID"""
    try:
        submission = Submission.query.filter_by(job_id=job_id).first()
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        response_data = submission.to_dict()
        
        # Include analysis results if available
        if submission.analysis_result:
            response_data['analysis_available'] = True
            response_data['analysis_summary'] = {
                'word_count': submission.analysis_result.content_statistics.get('word_count') if submission.analysis_result.content_statistics else None,
                'readability_score': submission.analysis_result.flesch_kincaid_score,
                'timeliness': submission.analysis_result.timeliness_classification.value if submission.analysis_result.timeliness_classification else None
            }
        else:
            response_data['analysis_available'] = False
        
        return jsonify(response_data)
        
    except Exception as e:
        current_app.logger.error(f"Status check error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@submission_bp.route('/help/drive-permissions', methods=['GET'])
def drive_permission_help():
    """
    Provide guidance for Google Drive permission issues
    
    SRS Reference: M1.UC02 - Permission Guidance for Drive Retrieval
    """
    return jsonify({
        'title': 'Google Drive Permission Setup',
        'description': 'Follow these steps to make your Google Drive file accessible:',
        'steps': submission_service._get_permission_guidance()['steps'],
        'video_tutorial': '/static/videos/drive-permissions.mp4',
        'troubleshooting': {
            'still_not_working': [
                'Ensure you are signed in to the correct Google account',
                'Check if the file is in a shared drive (different permissions)',
                'Try using the direct file link instead of folder link',
                'Contact your instructor if file sharing is restricted'
            ]
        }
    })

@submission_bp.route('/validate-link', methods=['POST'])
def validate_drive_link():
    """Validate Google Drive link without downloading"""
    try:
        data = request.get_json()
        
        if not data or 'drive_link' not in data:
            return jsonify({'error': 'Google Drive link is required'}), 400
        
        drive_link = data['drive_link'].strip()
        
        # Validate link format
        file_id, validation_error = submission_service.validate_drive_link(drive_link)
        if validation_error:
            return jsonify({
                'valid': False,
                'error': validation_error
            }), 200
        
        # Check file accessibility
        metadata, error = submission_service.get_drive_file_metadata(file_id)
        
        if error:
            return jsonify({
                'valid': False,
                'error': error['message'],
                'error_type': error.get('error_type'),
                'guidance': error.get('guidance')
            }), 200
        
        # Check file type
        if metadata['mimeType'] not in submission_service.allowed_mime_types:
            return jsonify({
                'valid': False,
                'error': f"Unsupported file type: {metadata['mimeType']}",
                'supported_types': list(submission_service.allowed_mime_types)
            }), 200
        
        return jsonify({
            'valid': True,
            'file_info': {
                'name': metadata['name'],
                'type': metadata['mimeType'],
                'size': metadata.get('size'),
                'created_time': metadata.get('createdTime'),
                'modified_time': metadata.get('modifiedTime')
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Link validation error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
