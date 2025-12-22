"""
Heuristic Insights Service - Handles rule-based insights and deadline analysis

Extracted from api/insights.py to follow proper service layer architecture.
"""

import pytz
from datetime import datetime, timedelta
from flask import current_app

from app.models import DocumentSnapshot, TimelinesssClassification


class InsightsService:
    """Service for generating rule-based insights and deadline analysis"""
    
    def __init__(self):
        self.last_minute_threshold_hours = 1  # SRS: < 1 hour = last minute rush
        self.major_contribution_threshold = 50  # SRS: ≥50% = major contribution
    
    def evaluate_submission_timeliness(self, submission, deadline=None):
        """Evaluate timeliness of submission against deadline"""
        if not deadline:
            return {
                'classification': TimelinesssClassification.NO_DEADLINE,
                'message': 'No deadline set for this submission',
                'details': None
            }
        
        try:
            submission_time = None
            
            if submission.analysis_result and submission.analysis_result.document_metadata:
                metadata = submission.analysis_result.document_metadata
                if metadata.get('last_modified_date'):
                    submission_time = datetime.fromisoformat(metadata['last_modified_date'].replace('Z', '+00:00'))
            
            if not submission_time:
                submission_time = submission.created_at
            
            if submission_time.tzinfo is None:
                submission_time = pytz.UTC.localize(submission_time)
            
            deadline_time = deadline.deadline_datetime
            if deadline_time.tzinfo is None:
                if request_tz := getattr(deadline, 'timezone', None):
                    if request_tz and request_tz != 'UTC':
                        try:
                            local_tz = pytz.timezone(request_tz)
                            deadline_time = local_tz.localize(deadline_time)
                        except Exception:
                            deadline_time = pytz.UTC.localize(deadline_time)
                    else:
                        deadline_time = pytz.UTC.localize(deadline_time)
                else:
                    deadline_time = pytz.UTC.localize(deadline_time)
            
            submission_time = submission_time.astimezone(pytz.UTC)
            deadline_time = deadline_time.astimezone(pytz.UTC)
            
            time_difference = submission_time - deadline_time
            
            if time_difference <= timedelta(0):
                time_before_deadline = abs(time_difference)
                
                if time_before_deadline <= timedelta(hours=self.last_minute_threshold_hours):
                    classification = TimelinesssClassification.LAST_MINUTE_RUSH
                    message = f"Last-minute submission (submitted {self._format_time_difference(time_before_deadline)} before deadline)"
                else:
                    classification = TimelinesssClassification.ON_TIME
                    message = f"On-time submission (submitted {self._format_time_difference(time_before_deadline)} before deadline)"
            else:
                classification = TimelinesssClassification.LATE
                message = f"Late submission (submitted {self._format_time_difference(time_difference)} after deadline)"
            
            return {
                'classification': classification,
                'message': message,
                'details': {
                    'submission_time': submission_time.isoformat(),
                    'deadline_time': deadline_time.isoformat(),
                    'time_difference_minutes': int(time_difference.total_seconds() / 60),
                    'is_late': time_difference > timedelta(0),
                    'is_last_minute': (
                        time_difference <= timedelta(0) and 
                        abs(time_difference) <= timedelta(hours=self.last_minute_threshold_hours)
                    )
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Timeliness evaluation error: {e}")
            return {
                'classification': TimelinesssClassification.NO_DEADLINE,
                'message': f'Error evaluating timeliness: {e}',
                'details': None
            }
    
    def compute_contribution_growth(self, submission):
        """Compute contribution growth between document versions"""
        try:
            current_snapshot = DocumentSnapshot.query.filter_by(
                submission_id=submission.id
            ).order_by(DocumentSnapshot.created_at.desc()).first()
            
            if not current_snapshot:
                return {
                    'has_comparison': False,
                    'message': 'No version history available',
                    'current_word_count': 0,
                    'previous_word_count': None,
                    'change_percentage': None,
                    'is_major_contribution': False
                }
            
            previous_snapshot = DocumentSnapshot.query.filter_by(
                file_id=current_snapshot.file_id
            ).filter(
                DocumentSnapshot.id != current_snapshot.id
            ).order_by(DocumentSnapshot.created_at.desc()).first()
            
            if not previous_snapshot:
                return {
                    'has_comparison': False,
                    'message': 'No prior version available for comparison',
                    'current_word_count': current_snapshot.word_count,
                    'previous_word_count': None,
                    'change_percentage': None,
                    'is_major_contribution': False
                }
            
            word_count_change = current_snapshot.word_count - previous_snapshot.word_count
            
            if previous_snapshot.word_count > 0:
                change_percentage = (word_count_change / previous_snapshot.word_count) * 100
            else:
                change_percentage = 100 if current_snapshot.word_count > 0 else 0
            
            is_major_contribution = abs(change_percentage) >= self.major_contribution_threshold
            
            return {
                'has_comparison': True,
                'message': f"Document changed by {change_percentage:.1f}%",
                'current_word_count': current_snapshot.word_count,
                'previous_word_count': previous_snapshot.word_count,
                'word_count_change': word_count_change,
                'change_percentage': round(change_percentage, 2),
                'is_major_contribution': is_major_contribution,
                'contribution_type': self._classify_contribution_type(change_percentage)
            }
            
        except Exception as e:
            current_app.logger.error(f"Contribution growth computation error: {e}")
            return {
                'has_comparison': False,
                'message': f'Error computing contribution: {e}',
                'current_word_count': 0,
                'previous_word_count': None,
                'change_percentage': None,
                'is_major_contribution': False
            }
    
    def _format_time_difference(self, time_delta):
        """Format time difference in human-readable format"""
        total_seconds = int(time_delta.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} seconds"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if minutes > 0:
                return f"{hours} hour{'s' if hours != 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''}"
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            if hours > 0:
                return f"{days} day{'s' if days != 1 else ''} and {hours} hour{'s' if hours != 1 else ''}"
            return f"{days} day{'s' if days != 1 else ''}"
    
    def _classify_contribution_type(self, change_percentage):
        """Classify contribution based on percentage change"""
        abs_change = abs(change_percentage)
        
        if abs_change >= 100:
            return 'Complete Rewrite'
        elif abs_change >= 50:
            return 'Major Revision'
        elif abs_change >= 20:
            return 'Significant Changes'
        elif abs_change >= 10:
            return 'Moderate Changes'
        elif abs_change >= 5:
            return 'Minor Changes'
        else:
            return 'Minimal Changes'
