"""
Submission-related Data Transfer Objects
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class SubmissionDTO:
    """Base DTO for Submission model serialization"""
    
    @staticmethod
    def serialize(submission, include_analysis: bool = False) -> Dict[str, Any]:
        """Serialize Submission model to dictionary"""
        if not submission:
            return None
        
        created_at_iso = submission.created_at.isoformat()
        if not created_at_iso.endswith('Z') and '+' not in created_at_iso:
            created_at_iso += 'Z'
        
        last_modified = submission.updated_at if submission.updated_at else submission.created_at
        last_modified_iso = last_modified.isoformat() if last_modified else None
        if last_modified_iso and not last_modified_iso.endswith('Z') and '+' not in last_modified_iso:
            last_modified_iso += 'Z'
        
        data = {
            'id': submission.id,
            'job_id': submission.job_id,
            'file_name': submission.file_name,
            'original_filename': submission.original_filename,
            'file_size': submission.file_size,
            'mime_type': submission.mime_type,
            'submission_type': submission.submission_type,
            'student_id': submission.student_id,
            'student_name': submission.student_name,
            'status': submission.status.value if hasattr(submission.status, 'value') else submission.status,
            'is_late': submission.is_late if hasattr(submission, 'is_late') else False,
            'created_at': created_at_iso,
            'last_modified': last_modified_iso
        }
        
        if submission.google_drive_link:
            data['google_drive_link'] = submission.google_drive_link
        
        if submission.deadline_id:
            data['deadline_id'] = submission.deadline_id
        
        if submission.error_message:
            data['error_message'] = submission.error_message
        
        if include_analysis and hasattr(submission, 'analysis_summary'):
            data['analysis_summary'] = submission.analysis_summary
        
        return data
    
    @staticmethod
    def serialize_list(submissions) -> List[Dict[str, Any]]:
        """Serialize list of Submission models"""
        return [SubmissionDTO.serialize(sub) for sub in submissions]


class SubmissionListDTO:
    """DTO for submission list view with minimal data"""
    
    @staticmethod
    def serialize(submission) -> Dict[str, Any]:
        """Serialize submission for list view"""
        if not submission:
            return None
        
        created_at_iso = submission.created_at.isoformat()
        if not created_at_iso.endswith('Z') and '+' not in created_at_iso:
            created_at_iso += 'Z'
        
        # Get word count from analysis result if available
        word_count = None
        if hasattr(submission, 'analysis_result') and submission.analysis_result:
            if submission.analysis_result.content_statistics:
                word_count = submission.analysis_result.content_statistics.get('word_count')
        
        data = {
            'id': submission.id,
            'job_id': submission.job_id,
            'file_name': submission.file_name,
            'original_filename': submission.original_filename,
            'student_id': submission.student_id,
            'student_name': submission.student_name,
            'status': submission.status.value if hasattr(submission.status, 'value') else submission.status,
            'is_late': submission.is_late if hasattr(submission, 'is_late') else False,
            'created_at': created_at_iso,
            'file_size': submission.file_size,
            'submission_type': submission.submission_type
        }
        
        # Add analysis summary if word count is available
        if word_count is not None:
            data['analysis_summary'] = {'word_count': word_count}
        
        return data
    
    @staticmethod
    def serialize_list(submissions) -> List[Dict[str, Any]]:
        """Serialize list of submissions for list view"""
        return [SubmissionListDTO.serialize(sub) for sub in submissions]


class SubmissionDetailDTO:
    """DTO for detailed submission view with full information"""
    
    @staticmethod
    def serialize(submission) -> Dict[str, Any]:
        """Serialize submission with full details"""
        if not submission:
            return None
        
        created_at_iso = submission.created_at.isoformat()
        if not created_at_iso.endswith('Z') and '+' not in created_at_iso:
            created_at_iso += 'Z'
        
        last_modified = submission.updated_at if submission.updated_at else submission.created_at
        last_modified_iso = last_modified.isoformat() if last_modified else None
        if last_modified_iso and not last_modified_iso.endswith('Z') and '+' not in last_modified_iso:
            last_modified_iso += 'Z'
        
        started_at_iso = submission.processing_started_at.isoformat() if submission.processing_started_at else None
        if started_at_iso and not started_at_iso.endswith('Z') and '+' not in started_at_iso:
            started_at_iso += 'Z'
        
        completed_at_iso = submission.processing_completed_at.isoformat() if submission.processing_completed_at else None
        if completed_at_iso and not completed_at_iso.endswith('Z') and '+' not in completed_at_iso:
            completed_at_iso += 'Z'
        
        data = {
            'id': submission.id,
            'job_id': submission.job_id,
            'file_name': submission.file_name,
            'original_filename': submission.original_filename,
            'file_path': submission.file_path,
            'file_size': submission.file_size,
            'file_hash': submission.file_hash,
            'mime_type': submission.mime_type,
            'submission_type': submission.submission_type,
            'google_drive_link': submission.google_drive_link,
            'student_id': submission.student_id,
            'student_name': submission.student_name,
            'status': submission.status.value if hasattr(submission.status, 'value') else submission.status,
            'is_late': submission.is_late if hasattr(submission, 'is_late') else False,
            'created_at': created_at_iso,
            'last_modified': last_modified_iso,
            'processing_started_at': started_at_iso,
            'processing_completed_at': completed_at_iso,
            'error_message': submission.error_message,
            'professor_id': submission.professor_id,
            'deadline_id': submission.deadline_id
        }
        
        if hasattr(submission, 'analysis_summary'):
            data['analysis_summary'] = submission.analysis_summary
        
        if hasattr(submission, 'analysis_result') and submission.analysis_result:
            from .analysis_dto import AnalysisResultDTO
            data['analysis_result'] = AnalysisResultDTO.serialize(submission.analysis_result)
        
        if hasattr(submission, 'deadline') and submission.deadline:
            from .deadline_dto import DeadlineDTO
            data['deadline'] = DeadlineDTO.serialize(submission.deadline)
        
        return data


class SubmissionTokenDTO:
    """DTO for Submission Token serialization"""
    
    @staticmethod
    def serialize(token) -> Dict[str, Any]:
        """Serialize SubmissionToken model"""
        if not token:
            return None
        
        return {
            'id': token.id,
            'token': token.token,
            'expires_at': token.expires_at.isoformat() if token.expires_at else None,
            'is_active': token.is_active,
            'usage_count': token.usage_count,
            'max_usage': token.max_usage,
            'deadline_id': token.deadline_id,
            'created_at': token.created_at.isoformat() if hasattr(token, 'created_at') else None
        }
    
    @staticmethod
    def serialize_list(tokens) -> List[Dict[str, Any]]:
        """Serialize list of tokens"""
        return [SubmissionTokenDTO.serialize(token) for token in tokens]
