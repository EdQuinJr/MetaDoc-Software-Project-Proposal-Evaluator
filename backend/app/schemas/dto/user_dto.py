"""
User-related Data Transfer Objects
"""

from typing import Optional, Dict, Any
from datetime import datetime


class UserDTO:
    """DTO for User model serialization"""
    
    @staticmethod
    def serialize(user) -> Dict[str, Any]:
        """Serialize User model to dictionary"""
        if not user:
            return None
        
        return {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role.value if hasattr(user.role, 'value') else user.role,
            'profile_picture': user.profile_picture,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }
    
    @staticmethod
    def serialize_list(users) -> list:
        """Serialize list of User models"""
        return [UserDTO.serialize(user) for user in users]


class UserProfileDTO:
    """DTO for detailed user profile with statistics"""
    
    @staticmethod
    def serialize(user, include_stats: bool = True) -> Dict[str, Any]:
        """Serialize user profile with optional statistics"""
        if not user:
            return None
        
        profile = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role.value if hasattr(user.role, 'value') else user.role,
            'profile_picture': user.profile_picture,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }
        
        if include_stats and hasattr(user, 'submissions'):
            profile['statistics'] = {
                'total_submissions': len(user.submissions) if user.submissions else 0,
                'total_deadlines': len(user.deadlines) if hasattr(user, 'deadlines') and user.deadlines else 0
            }
        
        return profile


class UserSessionDTO:
    """DTO for User Session serialization"""
    
    @staticmethod
    def serialize(session) -> Dict[str, Any]:
        """Serialize UserSession model to dictionary"""
        if not session:
            return None
        
        return {
            'id': session.id,
            'session_token': session.session_token,
            'user_id': session.user_id,
            'expires_at': session.expires_at.isoformat() if session.expires_at else None,
            'is_active': session.is_active,
            'created_at': session.created_at.isoformat() if hasattr(session, 'created_at') else None
        }
    
    @staticmethod
    def serialize_with_user(session, user) -> Dict[str, Any]:
        """Serialize session with user information"""
        if not session:
            return None
        
        session_data = UserSessionDTO.serialize(session)
        if user:
            session_data['user'] = UserDTO.serialize(user)
        
        return session_data
