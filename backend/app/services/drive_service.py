"""
Google Drive Service - Handles Google Drive API integration

Extracted from api/submission.py to follow proper service layer architecture.
"""

import os
from flask import current_app
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DriveService:
    """Service class for Google Drive API integration"""
    
    def __init__(self):
        self._service = None
    
    def _get_drive_service(self):
        """Initialize Google Drive API service (lazy initialization)"""
        if self._service:
            return self._service
            
        try:
            credentials = service_account.Credentials.from_service_account_file(
                current_app.config['GOOGLE_SERVICE_ACCOUNT_FILE'],
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            self._service = build('drive', 'v3', credentials=credentials)
            return self._service
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Google Drive service: {e}")
            raise Exception("Google Drive service unavailable")
    
    def get_file_metadata(self, file_id):
        """Get file metadata from Google Drive"""
        try:
            service = self._get_drive_service()
            
            # Get file metadata
            metadata = service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,size,createdTime,modifiedTime,owners,lastModifyingUser,permissions'
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
    
    def download_file(self, file_id, filename, mime_type=None):
        """Download file from Google Drive to temporary storage"""
        try:
            service = self._get_drive_service()
            
            # For Google Docs (based on mime_type), export as DOCX
            if mime_type == 'application/vnd.google-apps.document' or filename.endswith('.gdoc'):
                request_obj = service.files().export_media(
                    fileId=file_id,
                    mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                if not filename.endswith('.docx'):
                   filename = filename.replace('.gdoc', '.docx') if filename.endswith('.gdoc') else filename + '.docx'
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
