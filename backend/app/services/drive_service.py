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
    
    def _get_drive_service(self, user_credentials_json=None):
        """Initialize Google Drive API service (lazy initialization)"""
        # Always prioritize user credentials if provided (for accessing user-specific files)
        if user_credentials_json:
             try:
                 import json
                 from google.oauth2.credentials import Credentials
                 creds_dict = json.loads(user_credentials_json)
                 creds = Credentials.from_authorized_user_info(creds_dict)
                 return build('drive', 'v3', credentials=creds)
             except Exception as e:
                 current_app.logger.error(f"Failed to create service from user credentials: {e}")
                 # Fallthrough to service account
        
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
    
    def get_file_metadata(self, file_id, user_credentials_json=None):
        """Get file metadata from Google Drive"""
        try:
            try:
                service = self._get_drive_service(user_credentials_json)
            except Exception as service_error:
                # If service account is missing or fails, try to scrape public title
                current_app.logger.warning(f"Service account unavailable ({service_error}), attempting public metadata scrape")
                
                file_name = 'Google_Drive_File.docx'
                try:
                    import urllib.request
                    import re
                    # Try to fetch title from public link
                    url = f"https://docs.google.com/document/d/{file_id}/preview"
                    
                    # Use a standard User-Agent to avoid being blocked
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    req = urllib.request.Request(url, headers=headers)
                    
                    with urllib.request.urlopen(req, timeout=5) as response:
                        html_content = response.read().decode('utf-8', errors='ignore')
                        
                        # Try multiple patterns
                        patterns = [
                            r'<title>(.*?) - Google Docs</title>',
                            r'<meta property="og:title" content="(.*?)">',
                            r'<meta name="title" content="(.*?)">'
                        ]
                        
                        found_title = None
                        for pattern in patterns:
                            match = re.search(pattern, html_content)
                            if match:
                                found_title = match.group(1)
                                break
                        
                        if found_title:
                            # Clean up title
                            found_title = found_title.strip()
                            if not found_title.endswith('.docx'):
                                found_title += '.docx'
                            file_name = found_title
                            current_app.logger.info(f"Scraped public title: {file_name}")

                except Exception as scrape_err:
                    current_app.logger.warning(f"Public title scrape failed: {scrape_err}")

                return {
                    'id': file_id,
                    'name': file_name,
                    'mimeType': 'application/vnd.google-apps.document' 
                }, None
            
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
            # Fallback: Try downloading as a public file if API fails (no service account or permission error)
            # This works for files shared as "Anyone with link"
            try:
                current_app.logger.info(f"Attempting public download fallback for {file_id}")
                
                # Construct export URL for Docs or direct link for files
                if mime_type == 'application/vnd.google-apps.document':
                    url = f"https://docs.google.com/document/d/{file_id}/export?format=docx"
                else:
                    url = f"https://drive.google.com/uc?id={file_id}&export=download"
                
                import requests
                response = requests.get(url, allow_redirects=True)
                
                if response.status_code == 200:
                    # Save to temporary storage
                    if not filename.endswith('.docx') and mime_type == 'application/vnd.google-apps.document':
                         filename += '.docx'
                         
                    temp_path = os.path.join(current_app.config['TEMP_STORAGE_PATH'], filename)
                    with open(temp_path, 'wb') as f:
                        f.write(response.content)
                    return temp_path, None
            except Exception as fallback_error:
                current_app.logger.error(f"Public fallback failed: {fallback_error}")

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
