"""
Submission request/response schemas
"""

from typing import Optional

class SubmissionUploadSchema:
    """Schema for file upload submission validation"""
    
    required_fields = []  # File is required but handled separately
    optional_fields = ['student_id', 'student_name', 'deadline_id']
    
    @staticmethod
    def validate(data: dict, file_present: bool = False) -> tuple[bool, Optional[str]]:
        """Validate file upload request"""
        if not file_present:
            return False, "No file provided in request"
        
        if data is None:
            data = {}
        
        # Validate student_id format if provided
        if 'student_id' in data and data['student_id']:
            student_id = str(data['student_id']).strip()
            if not student_id:
                return False, "student_id cannot be empty if provided"
        
        # Validate student_name if provided
        if 'student_name' in data and data['student_name']:
            student_name = str(data['student_name']).strip()
            if not student_name:
                return False, "student_name cannot be empty if provided"
        
        return True, None


class DriveLinkSchema:
    """Schema for Google Drive link submission validation"""
    
    required_fields = ['drive_link']
    optional_fields = ['student_id', 'student_name', 'deadline_id']
    
    @staticmethod
    def validate(data: dict) -> tuple[bool, Optional[str]]:
        """Validate Google Drive link submission"""
        if not data:
            return False, "Request body is required"
        
        missing = [f for f in DriveLinkSchema.required_fields if f not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        drive_link = data.get('drive_link', '').strip()
        if not drive_link:
            return False, "drive_link cannot be empty"
        
        # Basic Google Drive URL validation
        if not ('drive.google.com' in drive_link or 'docs.google.com' in drive_link):
            return False, "Invalid Google Drive URL format"
        
        return True, None
