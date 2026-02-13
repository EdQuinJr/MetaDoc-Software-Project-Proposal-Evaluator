"""
Dashboard Module for MetaDoc

Implements SRS requirements:
- M5.UC02: View Submission Report (Dashboard)
- M5.UC03: Export Report (PDF / CSV)
- Deadline management
- Report viewing and filtering
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, send_file

from sqlalchemy import desc, asc, and_, or_
import pytz
import os

from app.core.extensions import db
from app.models import (
    Submission, AnalysisResult, Deadline, User, DocumentSnapshot, AuditLog,
    SubmissionStatus, TimelinesssClassification
)
from app.services.audit_service import AuditService
from app.services import DashboardService
from app.api.auth import get_auth_service
from app.utils.decorators import require_authentication
from app.schemas.dto import (
    SubmissionListDTO, SubmissionDetailDTO, DeadlineDTO, DeadlineListDTO
)

dashboard_bp = Blueprint('dashboard', __name__)

# Initialize service
dashboard_service = None

def get_dashboard_service():
    global dashboard_service
    if dashboard_service is None:
        from app.services import DashboardService
        dashboard_service = DashboardService()
    return dashboard_service

# Lazy initialize
dashboard_service = get_dashboard_service()

@dashboard_bp.route('/overview', methods=['GET'])
@require_authentication()
def get_dashboard_overview():
    """
    Get dashboard overview with statistics
    
    SRS Reference: Dashboard functionality for professor interface
    """
    try:
        user_id = request.current_user.id
        
        overview_data, error = dashboard_service.get_dashboard_overview(user_id)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify(overview_data)
        
    except Exception as e:
        current_app.logger.error(f"Dashboard overview error: {e}")
        return jsonify({'error': 'Error loading dashboard'}), 500

@dashboard_bp.route('/submissions', methods=['GET'])
@require_authentication()
def get_submissions():
    """
    Get submissions list with filtering and pagination
    
    SRS Reference: M5.UC02 - View Submission Report
    """
    try:
        user_id = request.current_user.id
        
        # Parse query parameters
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('deadline_id'):
            filters['deadline_id'] = request.args.get('deadline_id')
        if request.args.get('student_id'):
            filters['student_id'] = request.args.get('student_id')
        if request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')
        if request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        if request.args.get('timeliness'):
            filters['timeliness'] = request.args.get('timeliness')
        if request.args.get('sort_by'):
            filters['sort_by'] = request.args.get('sort_by')
        if request.args.get('sort_order'):
            filters['sort_order'] = request.args.get('sort_order')
        
        # Parse pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        result, error = dashboard_service.get_submissions_list(
            user_id=user_id,
            filters=filters if filters else None,
            page=page,
            per_page=per_page
        )
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Submissions list error: {e}")
        return jsonify({'error': 'Error loading submissions'}), 500

@dashboard_bp.route('/submissions/<submission_id>', methods=['GET'])
@require_authentication()
def get_submission_detail(submission_id):
    """
    Get detailed submission information
    
    SRS Reference: M5.UC02 - View Submission Report (detailed view)
    """
    try:
        user_id = request.current_user.id
        
        submission, error = dashboard_service.get_submission_detail(submission_id, user_id)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 500
            
        # [Auto-Repair] Check if metadata is missing/incomplete
        # This fixes submissions that were processed before the metadata logic was improved
        try:
            # Force GDrive re-download if file is missing locally
            processing_path = submission.file_path
            if submission.google_drive_link and (not processing_path or not os.path.exists(processing_path)):
                current_app.logger.info(f"File missing for {submission.id}, attempting re-download from Drive link")
                try:
                    # Extract ID
                    file_id = None
                    if 'drive.google.com' in submission.google_drive_link or 'docs.google.com' in submission.google_drive_link:
                         import re
                         match = re.search(r'[-\w]{25,}', submission.google_drive_link)
                         if match: file_id = match.group()
                    
                    if file_id:
                        from app.services.drive_service import DriveService
                        drive_service = DriveService()
                        # Use generic name for temp processing
                        temp_path, _ = drive_service.download_file(file_id, "temp_reprocess.docx", "application/vnd.google-apps.document")
                        if temp_path and os.path.exists(temp_path):
                            processing_path = temp_path
                except Exception as dl_err:
                     current_app.logger.warning(f"Re-download failed: {dl_err}")

            if processing_path and os.path.exists(processing_path):
                needs_update = False
                if not submission.analysis_result:
                    needs_update = True
                if submission.analysis_result and submission.analysis_result.document_metadata:
                    meta = submission.analysis_result.document_metadata
                    # Check if key fields are unavailable
                    if meta.get('author') == 'Unavailable' and meta.get('last_editor') == 'Unavailable':
                         needs_update = True
                    # [Correction] If Author is currently set to Student Name, force re-check
                    # This fixes records where Student Name was incorrectly assigned as Author
                    elif submission.student_name and meta.get('author') == submission.student_name:
                        needs_update = True
                
                if needs_update:
                    current_app.logger.info(f"Auto-repairing metadata for submission {submission.id}")
                    from app.services.metadata_service import MetadataService
                    meta_service = MetadataService()
                    
                    # Re-extract
                    new_metadata, err = meta_service.extract_docx_metadata(processing_path)
                    
                    if not err and new_metadata:
                        # [GDrive Enhancement] Try to fetch real owner info if it's a Drive link
                        if submission.google_drive_link:
                            try:
                                # Extract ID from link
                                file_id = None
                                if 'drive.google.com' in submission.google_drive_link or 'docs.google.com' in submission.google_drive_link:
                                    import re
                                    # Simple regex for ID (alphanumeric, -, _)
                                    match = re.search(r'[-\w]{25,}', submission.google_drive_link)
                                    if match:
                                        file_id = match.group()
                                
                                if file_id:
                                    from app.services.drive_service import DriveService
                                    from flask import session
                                    drive_service = DriveService()
                                    
                                    # Use logged-in user's credentials if available to get better metadata (like emails)
                                    user_creds = session.get('google_credentials')
                                    
                                    # Try to fetch GDrive metadata 
                                    g_meta, g_error = drive_service.get_file_metadata(file_id, user_credentials_json=user_creds)
                                    
                                    if g_meta and not g_error:
                                        # [Title Repair] Update filename if we found a better one and current is generic
                                        if 'name' in g_meta and g_meta['name'] and g_meta['name'] != 'Google_Drive_File.docx':
                                            current_name = submission.original_filename
                                            # Check if current name is generic, hash version, or suspiciously short/default
                                            is_generic = (
                                                'Google_Drive_File' in current_name or 
                                                'submission' in current_name.lower() or
                                                current_name == 'file.docx'
                                            )
                                            
                                            if is_generic:
                                                current_app.logger.info(f"Renaming submission {submission.id} from {current_name} to {g_meta['name']}")
                                                submission.original_filename = g_meta['name']
                                                submission.file_name = g_meta['name'] # Update display name too
                                                db.session.add(submission)
                                                # Explicit commit for filename change
                                                db.session.commit()

                                        # Got real GDrive data!
                                        if 'owners' in g_meta and g_meta['owners']:
                                            owner = g_meta['owners'][0]
                                            owner_display = f"{owner.get('displayName')} ({owner.get('emailAddress')})"
                                            new_metadata['author'] = owner_display
                                            
                                            # Add to contributors
                                            new_metadata['contributors'] = [{
                                                'name': owner.get('displayName'),
                                                'email': owner.get('emailAddress'),
                                                'role': 'Owner (Google Drive)',
                                                'date': new_metadata.get('creation_date')
                                            }]
                                        
                                        if 'lastModifyingUser' in g_meta:
                                            mod_user = g_meta['lastModifyingUser']
                                            mod_display = f"{mod_user.get('displayName')} ({mod_user.get('emailAddress')})"
                                            new_metadata['last_editor'] = mod_display
                                            
                                            # Add unique editor to contributors
                                            if not new_metadata['contributors'] or new_metadata['contributors'][0].get('email') != mod_user.get('emailAddress'):
                                                new_metadata['contributors'].append({
                                                    'name': mod_user.get('displayName'),
                                                    'email': mod_user.get('emailAddress'),
                                                    'role': 'Last Editor (Google Drive)',
                                                    'date': new_metadata.get('last_modified_date')
                                                })

                            except Exception as drive_err:
                                current_app.logger.warning(f"Could not fetch GDrive specific metadata: {drive_err}")

                        # [Fallback] Use Student Name from submission if Author is still Unavailable
                        # ONLY for direct file uploads. For Google Drive, we prefer 'Unavailable' over incorrect attribution
                        # unless the user strictly requested otherwise.
                        if submission.student_name and not submission.google_drive_link and new_metadata.get('author') == 'Unavailable':
                            new_metadata['author'] = submission.student_name
                            
                            if new_metadata.get('last_editor') == 'Unavailable':
                                new_metadata['last_editor'] = submission.student_name
                            
                            # Ensure contributors list has the student
                            has_student = False
                            if new_metadata.get('contributors'):
                                for c in new_metadata['contributors']:
                                    if c.get('name') == submission.student_name:
                                        has_student = True
                                        break
                            else:
                                new_metadata['contributors'] = []
                                
                            if not has_student:
                                new_metadata['contributors'].append({
                                    'name': submission.student_name,
                                    'role': 'Author (Student)',
                                    'date': new_metadata.get('creation_date')
                                })
                        
                        # Update DB
                        # ... rest of the update logic ...
                        from app.models import AnalysisResult
                        if not submission.analysis_result:
                            submission.analysis_result = AnalysisResult(submission_id=submission.id)
                            db.session.add(submission.analysis_result)
                        
                        submission.analysis_result.document_metadata = new_metadata
                        db.session.commit()
                        current_app.logger.info("Metadata auto-repaired successfully")
        except Exception as e:
            current_app.logger.error(f"Auto-repair failed (non-critical): {e}")

        # [Auto-Repair] Check if AI Rubric Evaluation is missing but required
        try:
            if submission.deadline and submission.deadline.rubric:
                needs_ai_repair = False
                if not submission.analysis_result:
                     needs_ai_repair = True 
                elif not submission.analysis_result.ai_insights:
                     needs_ai_repair = True
                elif 'rubric_evaluation' not in submission.analysis_result.ai_insights:
                     needs_ai_repair = True
                
                if needs_ai_repair:
                    current_app.logger.info(f"Auto-repairing AI analysis for submission {submission.id}")
                    
                    # Ensure we have text
                    doc_text = None
                    if submission.analysis_result and submission.analysis_result.document_text:
                        doc_text = submission.analysis_result.document_text
                    
                    # If no text, try to read from file (if we have path from previous step or original)
                    if not doc_text and processing_path and os.path.exists(processing_path):
                         from app.services.metadata_service import MetadataService
                         meta_service = MetadataService()
                         doc_text = meta_service.extract_document_text(processing_path)
                    
                    if doc_text:
                         from app.services.nlp_service import NLPService
                         nlp_service = NLPService()
                         
                         rubric_data = submission.deadline.rubric.to_dict()
                         context = {
                            'assignment_type': submission.deadline.assignment_type or 'General',
                            'student_level': 'Undergraduate' # Default
                         }
                         
                         ai_summary, ai_error = nlp_service.generate_ai_summary(doc_text, context, rubric=rubric_data)
                         
                         if ai_summary and not ai_error:
                             if not submission.analysis_result:
                                 from app.models import AnalysisResult
                                 submission.analysis_result = AnalysisResult(submission_id=submission.id)
                                 db.session.add(submission.analysis_result)
                             
                             submission.analysis_result.ai_summary = ai_summary.get('summary')
                             submission.analysis_result.ai_insights = ai_summary
                             
                             # If we just extracted text, save it too
                             if not submission.analysis_result.document_text:
                                 submission.analysis_result.document_text = doc_text
                                 
                             db.session.commit()
                             current_app.logger.info("AI analysis auto-repaired successfully")
                         else:
                             current_app.logger.warning(f"AI repair failed: {ai_error}")
                    else:
                        current_app.logger.warning("Cannot repair AI: No document text available")

        except Exception as e:
            current_app.logger.error(f"AI Auto-repair failed: {e}")

        # Serialize submission using DTO
        from app.schemas.dto import SubmissionDetailDTO
        return jsonify(SubmissionDetailDTO.serialize(submission))
        
    except Exception as e:
        current_app.logger.error(f"Submission detail error: {e}")
        return jsonify({'error': 'Error loading submission details'}), 500

@dashboard_bp.route('/deadlines', methods=['GET'])
@require_authentication()
def get_deadlines():
    """Get list of deadlines for the authenticated user"""
    try:
        user_id = request.current_user.id
        include_past = request.args.get('include_past', 'false').lower() == 'true'
        
        deadlines, error = dashboard_service.get_deadlines_list(user_id)
        
        if error:
            return jsonify({'error': error}), 500
        
        # Serialize deadlines using DTO
        from app.schemas.dto import DeadlineListDTO
        return jsonify({
            'deadlines': [DeadlineListDTO.serialize(d) for d in deadlines]
        })
        
    except Exception as e:
        current_app.logger.error(f"Deadlines list error: {e}")
        return jsonify({'error': 'Error loading deadlines'}), 500

@dashboard_bp.route('/deadlines', methods=['POST'])
@require_authentication()
def create_deadline():
    """Create a new deadline"""
    try:
        user_id = request.current_user.id
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('deadline_datetime'):
            return jsonify({'error': 'Title and deadline_datetime are required'}), 400
        
        deadline, error = dashboard_service.create_deadline(user_id, data)
        
        if error:
            return jsonify({'error': error}), 400
        
        from app.schemas.dto import DeadlineDTO
        return jsonify({
            'message': 'Deadline created successfully',
            'deadline': DeadlineDTO.serialize(deadline)
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Deadline creation error: {e}")
        return jsonify({'error': 'Error creating deadline'}), 500

@dashboard_bp.route('/deadlines/<deadline_id>', methods=['PUT'])
@require_authentication()
def update_deadline(deadline_id):
    """Update an existing deadline"""
    try:
        user_id = request.current_user.id
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No update data provided'}), 400
        
        deadline, error = dashboard_service.update_deadline(deadline_id, user_id, data)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 400
        
        from app.schemas.dto import DeadlineDTO
        return jsonify({
            'message': 'Deadline updated successfully',
            'deadline': DeadlineDTO.serialize(deadline)
        })
        
    except Exception as e:
        current_app.logger.error(f"Deadline update error: {e}")
        return jsonify({'error': 'Error updating deadline'}), 500

@dashboard_bp.route('/deadlines/<deadline_id>', methods=['DELETE'])
@require_authentication()
def delete_deadline(deadline_id):
    """Delete a deadline"""
    try:
        user_id = request.current_user.id
        
        success, error = dashboard_service.delete_deadline(deadline_id, user_id)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Deadline deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Deadline deletion error: {e}")
        return jsonify({'error': 'Error deleting deadline'}), 500

@dashboard_bp.route('/submissions/<submission_id>', methods=['DELETE'])
@require_authentication()
def delete_submission(submission_id):
    """Delete a submission"""
    try:
        user_id = request.current_user.id
        
        success, error = dashboard_service.delete_submission(submission_id, user_id)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Submission deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Submission deletion error: {e}")
        return jsonify({'error': 'Error deleting submission'}), 500


@dashboard_bp.route('/submissions/<submission_id>/download', methods=['GET'])
@require_authentication()
def download_submission_file(submission_id):
    """
    Download/View the submission file
    """
    try:
        user_id = request.current_user.id
        submission, error = dashboard_service.get_submission_detail(submission_id, user_id)
        
        if error:
             return jsonify({'error': error}), 404 if 'not found' in error else 500
             
        # Allow downloading of the local snapshot file even if it's a drive link
        # This provides a fallback if the link is inaccessible or if the user wants the analyzed version


        if not submission.file_path:
             return jsonify({'error': 'No file path associated with submission'}), 404
             
        # Ensure absolute path
        abs_file_path = os.path.abspath(submission.file_path)

        if not os.path.exists(abs_file_path):
             current_app.logger.error(f"File not found on disk: {abs_file_path}")
             return jsonify({'error': 'File not found on server'}), 404
             
        return send_file(
            abs_file_path,
            as_attachment=False, # View in browser if possible (inline)
            download_name=submission.original_filename,
            mimetype=submission.mime_type or 'application/pdf'
        )
    except Exception as e:
        import traceback
        current_app.logger.error(f"Download error: {e}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

@dashboard_bp.route('/deadlines/<deadline_id>/download-all', methods=['GET'])
@require_authentication()
def download_deadline_files(deadline_id):
    """
    Download all submission files for a deadline as a ZIP archive
    """
    try:
        user_id = request.current_user.id
        
        # Verify deadline ownership
        deadline = Deadline.query.filter_by(id=deadline_id, professor_id=user_id).first()
        if not deadline:
            return jsonify({'error': 'Deadline not found'}), 404
            
        submissions = Submission.query.filter_by(deadline_id=deadline_id).all()
        if not submissions:
            return jsonify({'error': 'No submissions found for this deadline'}), 404
            
        # Create ZIP in memory
        import zipfile
        import io
        
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            added_files = set()
            for sub in submissions:
                if sub.file_path and os.path.exists(sub.file_path):
                    # Create a unique filename for the zip
                    # Format: StudentName_OriginalName
                    student_prefix = sub.student_name.replace(' ', '_') if sub.student_name else sub.student_id or 'Unknown'
                    clean_filename = f"{student_prefix}_{sub.original_filename}".replace(' ', '_')
                    
                    # Handle duplicates in zip
                    if clean_filename in added_files:
                        name, ext = os.path.splitext(clean_filename)
                        clean_filename = f"{name}_{sub.id[:4]}{ext}"
                    
                    zf.write(sub.file_path, clean_filename)
                    added_files.add(clean_filename)
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            as_attachment=True,
            download_name=f"{deadline.title.replace(' ', '_')}_Submissions.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"Batch download error: {e}")
        return jsonify({'error': 'Error preparing batch download'}), 500


