"""
Dashboard Service - Handles dashboard operations and data aggregation

Extracted from api/dashboard.py to follow proper service layer architecture.
"""

from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import desc, and_
import pytz

from app.core.extensions import db
from app.models import (
    Submission, AnalysisResult, Deadline, DocumentSnapshot,
    SubmissionStatus, TimelinesssClassification
)


class DashboardService:
    """Service for dashboard operations and data aggregation"""
    
    def __init__(self):
        pass
    
    def get_dashboard_overview(self, user_id):
        """Get dashboard overview statistics for professor"""
        try:
            total_submissions = Submission.query.filter_by(professor_id=user_id).count()
            
            pending_submissions = Submission.query.filter_by(
                professor_id=user_id,
                status=SubmissionStatus.PENDING
            ).count()
            
            completed_submissions = Submission.query.filter_by(
                professor_id=user_id,
                status=SubmissionStatus.COMPLETED
            ).count()
            
            failed_submissions = Submission.query.filter_by(
                professor_id=user_id,
                status=SubmissionStatus.FAILED
            ).count()
            
            timeliness_stats = self._get_timeliness_statistics(user_id)
            recent_submissions = self._get_recent_submissions(user_id, limit=5)
            upcoming_deadlines = self._get_upcoming_deadlines(user_id, limit=3)
            
            # Count active deadlines (deadlines that haven't passed yet)
            now = datetime.utcnow()
            active_deadlines_count = Deadline.query.filter(
                Deadline.professor_id == user_id,
                Deadline.deadline_datetime >= now
            ).count()
            
            return {
                'total_submissions': total_submissions,
                'pending_submissions': pending_submissions,
                'completed_submissions': completed_submissions,
                'failed_submissions': failed_submissions,
                'active_deadlines': active_deadlines_count,
                'timeliness_statistics': timeliness_stats,
                'recent_submissions': recent_submissions,
                'upcoming_deadlines': upcoming_deadlines
            }, None
            
        except Exception as e:
            current_app.logger.error(f"Dashboard overview error: {e}")
            return None, str(e)
    
    def _get_timeliness_statistics(self, user_id):
        """Get timeliness classification statistics"""
        try:
            results = db.session.query(
                AnalysisResult.timeliness_classification,
                db.func.count(AnalysisResult.id)
            ).join(Submission).filter(
                Submission.professor_id == user_id,
                AnalysisResult.timeliness_classification.isnot(None)
            ).group_by(AnalysisResult.timeliness_classification).all()
            
            stats = {
                'on_time': 0,
                'late': 0,
                'last_minute': 0,
                'no_deadline': 0
            }
            
            for classification, count in results:
                if classification == TimelinesssClassification.ON_TIME:
                    stats['on_time'] = count
                elif classification == TimelinesssClassification.LATE:
                    stats['late'] = count
                elif classification == TimelinesssClassification.LAST_MINUTE_RUSH:
                    stats['last_minute'] = count
                elif classification == TimelinesssClassification.NO_DEADLINE:
                    stats['no_deadline'] = count
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Timeliness stats error: {e}")
            return {'on_time': 0, 'late': 0, 'last_minute': 0, 'no_deadline': 0}
    
    def _get_recent_submissions(self, user_id, limit=5):
        """Get recent submissions"""
        try:
            submissions = Submission.query.filter_by(
                professor_id=user_id
            ).order_by(desc(Submission.created_at)).limit(limit).all()
            
            return [{
                'id': s.id,
                'job_id': s.job_id,
                'file_name': s.original_filename,
                'student_name': s.student_name,
                'student_id': s.student_id,
                'status': s.status.value,
                'created_at': s.created_at.isoformat()
            } for s in submissions]
            
        except Exception as e:
            current_app.logger.error(f"Recent submissions error: {e}")
            return []
    
    def _get_upcoming_deadlines(self, user_id, limit=3):
        """Get upcoming deadlines"""
        try:
            now = datetime.utcnow()
            deadlines = Deadline.query.filter(
                Deadline.professor_id == user_id,
                Deadline.deadline_datetime >= now
            ).order_by(Deadline.deadline_datetime).limit(limit).all()
            
            return [{
                'id': d.id,
                'title': d.title,
                'deadline_datetime': d.deadline_datetime.isoformat(),
                'course_code': d.course_code,
                'submission_count': len(d.submissions) if d.submissions else 0
            } for d in deadlines]
            
        except Exception as e:
            current_app.logger.error(f"Upcoming deadlines error: {e}")
            return []
    
    def get_submissions_list(self, user_id, filters=None, page=1, per_page=20):
        """Get paginated list of submissions with filters"""
        try:
            query = Submission.query.filter_by(professor_id=user_id)
            
            if filters:
                if filters.get('status'):
                    query = query.filter_by(status=SubmissionStatus[filters['status'].upper()])
                
                if filters.get('deadline_id'):
                    query = query.filter_by(deadline_id=filters['deadline_id'])
                
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        db.or_(
                            Submission.original_filename.ilike(search_term),
                            Submission.student_name.ilike(search_term),
                            Submission.student_id.ilike(search_term)
                        )
                    )
            
            query = query.order_by(desc(Submission.created_at))
            
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Serialize submissions to dictionaries
            from app.schemas.dto.submission_dto import SubmissionListDTO
            serialized_submissions = [SubmissionListDTO.serialize(s) for s in pagination.items]
            
            return {
                'submissions': serialized_submissions,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }, None
            
        except Exception as e:
            current_app.logger.error(f"Submissions list error: {e}")
            return None, str(e)
    
    def get_submission_detail(self, submission_id, user_id):
        """Get detailed submission information"""
        try:
            submission = Submission.query.filter_by(
                id=submission_id,
                professor_id=user_id
            ).first()
            
            if not submission:
                return None, "Submission not found"
            
            return submission, None
            
        except Exception as e:
            current_app.logger.error(f"Submission detail error: {e}")
            return None, str(e)
    
    def delete_submission(self, submission_id, user_id):
        """Delete a submission and its related data"""
        try:
            submission = Submission.query.filter_by(
                id=submission_id,
                professor_id=user_id
            ).first()
            
            if not submission:
                return False, "Submission not found"
            
            # Delete related analysis results first (foreign key constraint)
            if hasattr(submission, 'analysis_result') and submission.analysis_result:
                db.session.delete(submission.analysis_result)
            
            # Delete the physical file
            import os
            if submission.file_path and os.path.exists(submission.file_path):
                try:
                    os.remove(submission.file_path)
                except Exception as file_err:
                    current_app.logger.warning(f"Could not delete file: {file_err}")
            
            # Delete the submission record
            db.session.delete(submission)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Submission deletion error: {e}")
            return False, str(e)
    
    def create_deadline(self, user_id, deadline_data):
        """Create a new deadline"""
        try:
            deadline = Deadline(
                professor_id=user_id,
                title=deadline_data['title'],
                description=deadline_data.get('description'),
                deadline_datetime=datetime.fromisoformat(deadline_data['deadline_datetime']),
                timezone=deadline_data.get('timezone', 'UTC'),
                course_code=deadline_data.get('course_code'),
                assignment_type=deadline_data.get('assignment_type'),
                rubric_id=deadline_data.get('rubric_id')
            )
            
            db.session.add(deadline)
            db.session.commit()
            
            return deadline, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Deadline creation error: {e}")
            return None, str(e)
    
    def update_deadline(self, deadline_id, user_id, deadline_data):
        """Update an existing deadline"""
        try:
            deadline = Deadline.query.filter_by(
                id=deadline_id,
                professor_id=user_id
            ).first()
            
            if not deadline:
                return None, "Deadline not found"
            
            if 'title' in deadline_data:
                deadline.title = deadline_data['title']
            if 'description' in deadline_data:
                deadline.description = deadline_data['description']
            if 'deadline_datetime' in deadline_data:
                deadline.deadline_datetime = datetime.fromisoformat(deadline_data['deadline_datetime'])
            if 'timezone' in deadline_data:
                deadline.timezone = deadline_data['timezone']
            if 'course_code' in deadline_data:
                deadline.course_code = deadline_data['course_code']
            if 'assignment_type' in deadline_data:
                deadline.assignment_type = deadline_data['assignment_type']
            if 'rubric_id' in deadline_data:
                deadline.rubric_id = deadline_data['rubric_id']
            
            db.session.commit()
            
            return deadline, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Deadline update error: {e}")
            return None, str(e)
    
    def delete_deadline(self, deadline_id, user_id):
        """Delete a deadline and all its submissions"""
        try:
            deadline = Deadline.query.filter_by(
                id=deadline_id,
                professor_id=user_id
            ).first()
            
            if not deadline:
                return False, "Deadline not found"
            
            # Get all submissions for this deadline
            submissions = Submission.query.filter_by(deadline_id=deadline_id).all()
            
            # Delete each submission and its related data
            import os
            for submission in submissions:
                # Delete related analysis results
                if hasattr(submission, 'analysis_result') and submission.analysis_result:
                    db.session.delete(submission.analysis_result)
                
                # Delete the physical file
                if submission.file_path and os.path.exists(submission.file_path):
                    try:
                        os.remove(submission.file_path)
                    except Exception as file_err:
                        current_app.logger.warning(f"Could not delete file: {file_err}")
                
                # Delete the submission record
                db.session.delete(submission)
            
            # Delete the deadline
            db.session.delete(deadline)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Deadline deletion error: {e}")
            return False, str(e)
    
    def get_deadlines_list(self, user_id):
        """Get all deadlines for a professor"""
        try:
            deadlines = Deadline.query.filter_by(
                professor_id=user_id
            ).order_by(Deadline.deadline_datetime).all()
            
            return deadlines, None
            
        except Exception as e:
            current_app.logger.error(f"Deadlines list error: {e}")
            return None, str(e)
