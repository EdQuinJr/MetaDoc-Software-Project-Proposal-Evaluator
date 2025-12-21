"""
Deadline request/response schemas
"""

from typing import Optional
from datetime import datetime

class DeadlineCreateSchema:
    """Schema for deadline creation validation"""
    
    required_fields = ['title', 'deadline_datetime']
    optional_fields = ['description', 'timezone', 'course_code', 'assignment_type']
    
    @staticmethod
    def validate(data: dict) -> tuple[bool, Optional[str]]:
        """Validate deadline creation request"""
        if not data:
            return False, "Request body is required"
        
        missing = [f for f in DeadlineCreateSchema.required_fields if f not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        if not data.get('title') or not data.get('title').strip():
            return False, "Title cannot be empty"
        
        if not data.get('deadline_datetime'):
            return False, "deadline_datetime is required"
        
        # Validate datetime format
        try:
            datetime.fromisoformat(data['deadline_datetime'])
        except (ValueError, TypeError):
            return False, "Invalid deadline_datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        
        return True, None


class DeadlineUpdateSchema:
    """Schema for deadline update validation"""
    
    required_fields = []  # All fields optional for update
    optional_fields = ['title', 'description', 'deadline_datetime', 'timezone', 'course_code', 'assignment_type']
    
    @staticmethod
    def validate(data: dict) -> tuple[bool, Optional[str]]:
        """Validate deadline update request"""
        if not data:
            return False, "Request body is required"
        
        # At least one field should be provided
        if not any(field in data for field in DeadlineUpdateSchema.optional_fields):
            return False, "At least one field must be provided for update"
        
        # Validate title if provided
        if 'title' in data and (not data['title'] or not data['title'].strip()):
            return False, "Title cannot be empty if provided"
        
        # Validate datetime format if provided
        if 'deadline_datetime' in data:
            try:
                datetime.fromisoformat(data['deadline_datetime'])
            except (ValueError, TypeError):
                return False, "Invalid deadline_datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        
        return True, None
