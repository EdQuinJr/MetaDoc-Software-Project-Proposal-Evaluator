"""
Authentication request/response schemas
"""

from typing import Optional

class LoginSchema:
    """Schema for login request validation"""
    
    required_fields = ['email', 'password']
    optional_fields = []
    
    @staticmethod
    def validate(data: dict) -> tuple[bool, Optional[str]]:
        """Validate login request data"""
        if not data:
            return False, "Request body is required"
        
        missing = [f for f in LoginSchema.required_fields if f not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        if not data.get('email'):
            return False, "Email cannot be empty"
        
        if not data.get('password'):
            return False, "Password cannot be empty"
        
        return True, None


class RegisterSchema:
    """Schema for user registration validation"""
    
    required_fields = ['email', 'name', 'password']
    optional_fields = ['role']
    
    @staticmethod
    def validate(data: dict) -> tuple[bool, Optional[str]]:
        """Validate registration request data"""
        if not data:
            return False, "Request body is required"
        
        missing = [f for f in RegisterSchema.required_fields if f not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        if not data.get('email') or '@' not in data.get('email', ''):
            return False, "Invalid email format"
        
        if not data.get('name'):
            return False, "Name cannot be empty"
        
        if not data.get('password') or len(data.get('password', '')) < 6:
            return False, "Password must be at least 6 characters"
        
        return True, None


class TokenGenerationSchema:
    """Schema for submission token generation"""
    
    required_fields = []
    optional_fields = ['deadline_id', 'max_usage']
    
    @staticmethod
    def validate(data: dict) -> tuple[bool, Optional[str]]:
        """Validate token generation request"""
        if data is None:
            data = {}
        
        if 'max_usage' in data:
            try:
                max_usage = int(data['max_usage'])
                if max_usage < 1:
                    return False, "max_usage must be at least 1"
            except (ValueError, TypeError):
                return False, "max_usage must be a valid integer"
        
        return True, None
