"""
Deadline-related Data Transfer Objects
"""

from typing import Optional, Dict, Any, List


class DeadlineDTO:
    """DTO for Deadline model serialization"""
    
    @staticmethod
    def serialize(deadline, include_submissions: bool = False) -> Dict[str, Any]:
        """Serialize Deadline model to dictionary"""
        if not deadline:
            return None
        
        data = {
            'id': deadline.id,
            'title': deadline.title,
            'description': deadline.description,
            'deadline_datetime': deadline.deadline_datetime.isoformat() if deadline.deadline_datetime else None,
            'timezone': deadline.timezone,
            'course_code': deadline.course_code,
            'assignment_type': deadline.assignment_type,
            'professor_id': deadline.professor_id,
            'created_at': deadline.created_at.isoformat() if hasattr(deadline, 'created_at') else None
        }
        
        if include_submissions and hasattr(deadline, 'submissions'):
            data['submission_count'] = len(deadline.submissions) if deadline.submissions else 0
            
            if deadline.submissions:
                on_time = sum(1 for sub in deadline.submissions if not (hasattr(sub, 'is_late') and sub.is_late))
                late = sum(1 for sub in deadline.submissions if hasattr(sub, 'is_late') and sub.is_late)
                
                data['submissions_summary'] = {
                    'total': len(deadline.submissions),
                    'on_time': on_time,
                    'late': late
                }
        
        return data
    
    @staticmethod
    def serialize_list(deadlines) -> List[Dict[str, Any]]:
        """Serialize list of Deadline models"""
        return [DeadlineDTO.serialize(deadline) for deadline in deadlines]


class DeadlineListDTO:
    """DTO for deadline list view with minimal data"""
    
    @staticmethod
    def serialize(deadline) -> Dict[str, Any]:
        """Serialize deadline for list view"""
        if not deadline:
            return None
        
        data = {
            'id': deadline.id,
            'title': deadline.title,
            'deadline_datetime': deadline.deadline_datetime.isoformat() if deadline.deadline_datetime else None,
            'timezone': deadline.timezone,
            'course_code': deadline.course_code,
            'assignment_type': deadline.assignment_type,
            'created_at': deadline.created_at.isoformat() if hasattr(deadline, 'created_at') else None
        }
        
        if hasattr(deadline, 'submissions'):
            data['submission_count'] = len(deadline.submissions) if deadline.submissions else 0
        
        return data
    
    @staticmethod
    def serialize_list(deadlines) -> List[Dict[str, Any]]:
        """Serialize list of deadlines for list view"""
        return [DeadlineListDTO.serialize(deadline) for deadline in deadlines]
