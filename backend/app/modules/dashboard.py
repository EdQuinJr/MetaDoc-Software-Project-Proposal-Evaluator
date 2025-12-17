"""
Dashboard Module for MetaDoc

Implements SRS requirements:
- M5.UC02: View Submission Report (Dashboard)
- M5.UC03: Export Report (PDF / CSV)
- Deadline management
- Report viewing and filtering
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import desc, asc, and_, or_
import pytz
import os

from app import db
from app.models import (
    Submission, AnalysisResult, Deadline, User, DocumentSnapshot, AuditLog,
    SubmissionStatus, TimelinesssClassification
)
from app.services.audit_service import AuditService
from app.modules.auth import get_auth_service

dashboard_bp = Blueprint('dashboard', __name__)

class DashboardService:
    """Service for dashboard operations and data aggregation"""
    
    def __init__(self):
        pass
    
    def get_dashboard_overview(self, user_id):
        """Get dashboard overview statistics for professor"""
        try:
            # Get submissions statistics
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
            
            # Get recent submissions
            recent_submissions = Submission.query.filter_by(
                professor_id=user_id
            ).order_by(desc(Submission.created_at)).limit(10).all()
            
            # Get deadline statistics
            active_deadlines = Deadline.query.filter_by(
                professor_id=user_id
            ).filter(
                Deadline.deadline_datetime > datetime.utcnow()
            ).count()
            
            # Get timeliness statistics
            timeliness_stats = self._get_timeliness_statistics(user_id)
            
            # Get processing performance
            avg_processing_time = db.session.query(
                db.func.avg(AnalysisResult.processing_duration_seconds)
            ).join(Submission).filter(
                Submission.professor_id == user_id,
                AnalysisResult.processing_duration_seconds.isnot(None)
            ).scalar()
            
            # Get upcoming deadlines (only 3 nearest)
            upcoming_deadlines = Deadline.query.filter_by(
                professor_id=user_id
            ).filter(
                Deadline.deadline_datetime > datetime.utcnow()
            ).order_by(Deadline.deadline_datetime.asc()).limit(3).all()
            
            return {
                'total_submissions': total_submissions,
                'pending_submissions': pending_submissions,
                'completed_submissions': completed_submissions,
                'failed_submissions': failed_submissions,
                'active_deadlines': active_deadlines,
                'completion_rate': round((completed_submissions / max(total_submissions, 1)) * 100, 1),
                'average_processing_time_seconds': round(avg_processing_time or 0, 2),
                
                'submission_statistics': {
                    'total': total_submissions,
                    'pending': pending_submissions,
                    'completed': completed_submissions,
                    'failed': failed_submissions,
                    'completion_rate': round((completed_submissions / max(total_submissions, 1)) * 100, 1)
                },
                'deadline_statistics': {
                    'active_deadlines': active_deadlines
                },
                'timeliness_statistics': timeliness_stats,
                'performance_metrics': {
                    'average_processing_time_seconds': round(avg_processing_time or 0, 2)
                },
                'recent_submissions': [
                    {
                        'id': s.id,
                        'job_id': s.job_id,
                        'original_filename': s.original_filename,
                        'student_id': s.student_id,
                        'status': s.status.value,
                        'created_at': s.created_at.isoformat(),
                        'file_size': s.file_size
                    } for s in recent_submissions
                ],
                'upcoming_deadlines': [
                    {
                        'id': d.id,
                        'title': d.title,
                        'deadline_datetime': d.deadline_datetime.isoformat(),
                        'submission_count': len([s for s in d.submissions if s.professor_id == user_id])
                    } for d in upcoming_deadlines
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"Dashboard overview error: {e}")
            raise
    
    def _get_timeliness_statistics(self, user_id):
        """Get timeliness statistics for user's submissions"""
        try:
            # Query submissions with analysis results
            submissions_with_analysis = db.session.query(
                AnalysisResult.timeliness_classification,
                db.func.count(AnalysisResult.id)
            ).join(Submission).filter(
                Submission.professor_id == user_id,
                AnalysisResult.timeliness_classification.isnot(None)
            ).group_by(AnalysisResult.timeliness_classification).all()
            
            stats = {
                'on_time': 0,
                'late': 0,
                'last_minute_rush': 0,
                'no_deadline': 0
            }
            
            for classification, count in submissions_with_analysis:
                if classification == TimelinesssClassification.ON_TIME:
                    stats['on_time'] = count
                elif classification == TimelinesssClassification.LATE:
                    stats['late'] = count
                elif classification == TimelinesssClassification.LAST_MINUTE_RUSH:
                    stats['last_minute_rush'] = count
                elif classification == TimelinesssClassification.NO_DEADLINE:
                    stats['no_deadline'] = count
            
            total = sum(stats.values())
            
            return {
                'counts': stats,
                'percentages': {
                    key: round((value / max(total, 1)) * 100, 1) 
                    for key, value in stats.items()
                },
                'total_analyzed': total
            }
            
        except Exception as e:
            current_app.logger.error(f"Timeliness statistics error: {e}")
            return {
                'counts': {'on_time': 0, 'late': 0, 'last_minute_rush': 0, 'no_deadline': 0},
                'percentages': {'on_time': 0, 'late': 0, 'last_minute_rush': 0, 'no_deadline': 0},
                'total_analyzed': 0
            }
    
    def get_submissions_list(self, user_id, filters=None, pagination=None):
        """Get filtered and paginated submissions list"""
        try:
            query = Submission.query.filter_by(professor_id=user_id)
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    query = query.filter(Submission.status == SubmissionStatus(filters['status']))
                
                if filters.get('deadline_id'):
                    query = query.filter(Submission.deadline_id == filters['deadline_id'])
                
                if filters.get('student_id'):
                    query = query.filter(
                        Submission.student_id.ilike(f"%{filters['student_id']}%")
                    )
                
                if filters.get('date_from'):
                    date_from = datetime.fromisoformat(filters['date_from'])
                    query = query.filter(Submission.created_at >= date_from)
                
                if filters.get('date_to'):
                    date_to = datetime.fromisoformat(filters['date_to'])
                    query = query.filter(Submission.created_at <= date_to)
                
                if filters.get('timeliness'):
                    query = query.join(AnalysisResult).filter(
                        AnalysisResult.timeliness_classification == TimelinesssClassification(filters['timeliness'])
                    )
            
            # Apply sorting
            sort_by = filters.get('sort_by', 'created_at') if filters else 'created_at'
            sort_order = filters.get('sort_order', 'desc') if filters else 'desc'
            
            if sort_by == 'created_at':
                query = query.order_by(desc(Submission.created_at) if sort_order == 'desc' else asc(Submission.created_at))
            elif sort_by == 'filename':
                query = query.order_by(desc(Submission.original_filename) if sort_order == 'desc' else asc(Submission.original_filename))
            elif sort_by == 'student_id':
                query = query.order_by(desc(Submission.student_id) if sort_order == 'desc' else asc(Submission.student_id))
            elif sort_by == 'file_size':
                query = query.order_by(desc(Submission.file_size) if sort_order == 'desc' else asc(Submission.file_size))
            
            # Apply pagination
            if pagination:
                page = pagination.get('page', 1)
                per_page = min(pagination.get('per_page', 20), 100)  # Max 100 per page
                
                paginated = query.paginate(
                    page=page,
                    per_page=per_page,
                    error_out=False
                )
                
                submissions = paginated.items
                pagination_info = {
                    'page': page,
                    'per_page': per_page,
                    'total': paginated.total,
                    'pages': paginated.pages,
                    'has_next': paginated.has_next,
                    'has_prev': paginated.has_prev
                }
            else:
                submissions = query.limit(100).all()  # Default limit
                pagination_info = None
            
            # Format submission data
            submission_data = []
            for submission in submissions:
                data = submission.to_dict()
                
                # Add analysis summary if available
                if submission.analysis_result:
                    analysis = submission.analysis_result
                    data['analysis_summary'] = {
                        'word_count': analysis.content_statistics.get('word_count') if analysis.content_statistics else None,
                        'flesch_kincaid_score': analysis.flesch_kincaid_score,
                        'readability_grade': analysis.readability_grade,
                        'timeliness_classification': analysis.timeliness_classification.value if analysis.timeliness_classification else None,
                        'is_complete': analysis.is_complete_document,
                        'warning_count': len(analysis.validation_warnings) if analysis.validation_warnings else 0
                    }
                else:
                    data['analysis_summary'] = None
                
                # Add deadline info
                if submission.deadline:
                    data['deadline_info'] = {
                        'title': submission.deadline.title,
                        'deadline_datetime': submission.deadline.deadline_datetime.isoformat(),
                        'course_code': submission.deadline.course_code
                    }
                else:
                    data['deadline_info'] = None
                
                submission_data.append(data)
            
            return {
                'submissions': submission_data,
                'pagination': pagination_info
            }
            
        except Exception as e:
            current_app.logger.error(f"Submissions list error: {e}")
            raise
    
    def get_submission_detail(self, submission_id, user_id):
        """Get detailed submission information with full analysis results"""
        try:
            submission = Submission.query.filter_by(
                id=submission_id,
                professor_id=user_id
            ).first()
            
            if not submission:
                return None, "Submission not found or access denied"
            
            # Get submission data
            detail_data = submission.to_dict()
            
            # Add analysis results
            if submission.analysis_result:
                analysis = submission.analysis_result
                detail_data['analysis_result'] = analysis.to_dict()
                
                # Remove large text field from API response by default
                if 'document_text' in detail_data['analysis_result']:
                    detail_data['analysis_result']['document_text_length'] = len(detail_data['analysis_result']['document_text'])
                    del detail_data['analysis_result']['document_text']
            
            # Add deadline information
            if submission.deadline:
                detail_data['deadline'] = submission.deadline.to_dict()
            
            # Add document snapshots
            snapshots = DocumentSnapshot.query.filter_by(
                submission_id=submission.id
            ).order_by(desc(DocumentSnapshot.created_at)).all()
            
            detail_data['version_history'] = [
                {
                    'id': s.id,
                    'timestamp': s.snapshot_timestamp.isoformat(),
                    'word_count': s.word_count,
                    'major_changes': s.major_changes,
                    'change_percentage': s.change_percentage
                } for s in snapshots
            ]
            
            # Log data access
            AuditService.log_data_access('view_detail', submission.id, user_id)
            
            return detail_data, None
            
        except Exception as e:
            current_app.logger.error(f"Submission detail error: {e}")
            return None, f"Error retrieving submission: {e}"
    
    def create_deadline(self, user_id, deadline_data):
        """Create a new deadline for assignments"""
        try:
            # Parse deadline datetime
            deadline_datetime = datetime.fromisoformat(deadline_data['deadline_datetime'])
            
            # Check for duplicate title
            existing_deadline = Deadline.query.filter_by(
                professor_id=user_id,
                title=deadline_data['title']
            ).first()
            
            if existing_deadline:
                return None, f"A deadline with the title '{deadline_data['title']}' already exists. Please use a unique title."

            # Create deadline
            deadline = Deadline(
                title=deadline_data['title'],
                description=deadline_data.get('description'),
                deadline_datetime=deadline_datetime,
                timezone=deadline_data.get('timezone', 'UTC'),
                course_code=deadline_data.get('course_code'),
                assignment_type=deadline_data.get('assignment_type'),
                professor_id=user_id
            )
            
            db.session.add(deadline)
            db.session.commit()
            
            # Log deadline creation
            AuditService.log_event(
                'deadline_created',
                f'Deadline created: {deadline.title}',
                user_id=user_id,
                metadata={
                    'deadline_id': deadline.id,
                    'deadline_datetime': deadline_datetime.isoformat(),
                    'course_code': deadline.course_code
                }
            )
            
            return deadline.to_dict(), None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Deadline creation error: {e}")
            return None, f"Error creating deadline: {e}"
    
    def update_deadline(self, deadline_id, user_id, update_data):
        """Update an existing deadline"""
        try:
            deadline = Deadline.query.filter_by(
                id=deadline_id,
                professor_id=user_id
            ).first()
            
            if not deadline:
                return None, "Deadline not found or access denied"
            
            # Validate deadline datetime if being updated - REMOVED to allow past deadlines
            # if 'deadline_datetime' in update_data:
            #     new_deadline_datetime = datetime.fromisoformat(update_data['deadline_datetime'])
            #     current_datetime = datetime.utcnow()
            #     if new_deadline_datetime <= current_datetime:
            #         return None, "Deadline cannot be set to a past date or current time. Please select a future date and time."
            
            # Update fields
            if 'title' in update_data:
                deadline.title = update_data['title']
            if 'description' in update_data:
                deadline.description = update_data['description']
            if 'deadline_datetime' in update_data:
                deadline.deadline_datetime = datetime.fromisoformat(update_data['deadline_datetime'])
            if 'timezone' in update_data:
                deadline.timezone = update_data['timezone']
            if 'course_code' in update_data:
                deadline.course_code = update_data['course_code']
            if 'assignment_type' in update_data:
                deadline.assignment_type = update_data['assignment_type']
            
            deadline.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Log deadline update
            AuditService.log_event(
                'deadline_updated',
                f'Deadline updated: {deadline.title}',
                user_id=user_id,
                metadata={
                    'deadline_id': deadline.id,
                    'updated_fields': list(update_data.keys())
                }
            )
            
            return deadline.to_dict(), None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Deadline update error: {e}")
            return None, f"Error updating deadline: {e}"
    
    def delete_submission(self, submission_id, user_id):
        """Delete a submission and its associated file"""
        try:
            submission = Submission.query.filter_by(
                id=submission_id,
                professor_id=user_id
            ).first()
            
            if not submission:
                return False, "Submission not found or access denied"
            
            # Delete associated file
            if submission.file_path and os.path.exists(submission.file_path):
                try:
                    os.remove(submission.file_path)
                    current_app.logger.info(f"Deleted file: {submission.file_path}")
                except Exception as e:
                    current_app.logger.warning(f"Could not delete file {submission.file_path}: {e}")
            
            # Delete analysis result if exists
            if submission.analysis_result:
                db.session.delete(submission.analysis_result)
            
            # Delete document snapshots
            DocumentSnapshot.query.filter_by(submission_id=submission_id).delete()
            
            # Delete audit logs
            AuditLog.query.filter_by(submission_id=submission_id).delete()
            
            # Delete the submission
            db.session.delete(submission)
            db.session.commit()
            
            # Log deletion
            AuditService.log_event(
                event_type='submission_deleted',
                description=f'Submission deleted: {submission.original_filename}',
                user_id=user_id,
                metadata={
                    'submission_id': submission_id,
                    'filename': submission.original_filename,
                    'student_id': submission.student_id
                }
            )
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Submission deletion error: {e}")
            return False, f"Error deleting submission: {e}"
    
    def delete_deadline(self, deadline_id, user_id):
        """Delete a deadline"""
        try:
            deadline = Deadline.query.filter_by(
                id=deadline_id,
                professor_id=user_id
            ).first()
            
            if not deadline:
                return False, "Deadline not found or access denied"
            
            # Check if there are submissions linked to this deadline
            submission_count = Submission.query.filter_by(deadline_id=deadline_id).count()
            
            if submission_count > 0:
                # Option 1: Prevent deletion if submissions exist
                # return False, f"Cannot delete deadline with {submission_count} linked submission(s). Please unlink submissions first."
                
                # Option 2: Unlink submissions (set deadline_id to None)
                Submission.query.filter_by(deadline_id=deadline_id).update({'deadline_id': None})
                current_app.logger.info(f"Unlinked {submission_count} submissions from deadline {deadline_id}")
            
            # Delete the deadline
            db.session.delete(deadline)
            db.session.commit()
            
            # Log deletion
            AuditService.log_event(
                event_type='deadline_deleted',
                description=f'Deadline deleted: {deadline.title}',
                user_id=user_id,
                metadata={
                    'deadline_id': deadline_id,
                    'title': deadline.title,
                    'unlinked_submissions': submission_count
                }
            )
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Deadline deletion error: {e}")
            return False, f"Error deleting deadline: {e}"
    
    def get_deadlines_list(self, user_id, include_past=False):
        """Get list of deadlines for user"""
        try:
            query = Deadline.query.filter_by(professor_id=user_id)
            
            if not include_past:
                query = query.filter(Deadline.deadline_datetime > datetime.utcnow())
            
            deadlines = query.order_by(asc(Deadline.deadline_datetime)).all()
            
            # Add submission counts for each deadline
            deadline_data = []
            for deadline in deadlines:
                data = deadline.to_dict()
                
                # Count submissions for this deadline
                submission_count = Submission.query.filter_by(deadline_id=deadline.id).count()
                data['submission_count'] = submission_count
                
                # Check if deadline has passed
                data['is_past'] = deadline.deadline_datetime < datetime.utcnow()
                
                deadline_data.append(data)
            
            return deadline_data, None
            
        except Exception as e:
            current_app.logger.error(f"Deadlines list error: {e}")
            return None, f"Error retrieving deadlines: {e}"

# Initialize service
dashboard_service = DashboardService()

def require_authentication():
    """Decorator to require authentication for dashboard endpoints"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                # Get session token from Authorization header
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Authentication required'}), 401
                
                session_token = auth_header[7:]
                
                # Validate session
                result, error = get_auth_service().validate_session(session_token)
                
                if error:
                    return jsonify({'error': error}), 401
                
                # Add user to request context
                request.current_user = result['user']
                request.current_session = result['session']
                
                return f(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"Authentication check failed: {e}")
                return jsonify({'error': 'Authentication error'}), 500
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@dashboard_bp.route('/overview', methods=['GET'])
@require_authentication()
def get_dashboard_overview():
    """
    Get dashboard overview with statistics
    
    SRS Reference: Dashboard functionality for professor interface
    """
    try:
        user_id = request.current_user.id
        
        overview_data = dashboard_service.get_dashboard_overview(user_id)
        
        return jsonify(overview_data)
        
    except Exception as e:
        current_app.logger.error(f"Dashboard overview error: {e}")
        return jsonify({'error': 'Error loading dashboard'}), 500

@dashboard_bp.route('/submissions', methods=['GET'])
@require_authentication()
def get_submissions():
    """
    Get submissions list with filtering and pagination
    
    SRS Reference: M5.UC02 - View Submission Report
    """
    try:
        user_id = request.current_user.id
        
        # Parse query parameters
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('deadline_id'):
            filters['deadline_id'] = request.args.get('deadline_id')
        if request.args.get('student_id'):
            filters['student_id'] = request.args.get('student_id')
        if request.args.get('date_from'):
            filters['date_from'] = request.args.get('date_from')
        if request.args.get('date_to'):
            filters['date_to'] = request.args.get('date_to')
        if request.args.get('timeliness'):
            filters['timeliness'] = request.args.get('timeliness')
        if request.args.get('sort_by'):
            filters['sort_by'] = request.args.get('sort_by')
        if request.args.get('sort_order'):
            filters['sort_order'] = request.args.get('sort_order')
        
        # Parse pagination
        pagination = {}
        if request.args.get('page'):
            pagination['page'] = int(request.args.get('page', 1))
        if request.args.get('per_page'):
            pagination['per_page'] = int(request.args.get('per_page', 20))
        
        result = dashboard_service.get_submissions_list(
            user_id=user_id,
            filters=filters if filters else None,
            pagination=pagination if pagination else None
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Submissions list error: {e}")
        return jsonify({'error': 'Error loading submissions'}), 500

@dashboard_bp.route('/submissions/<submission_id>', methods=['GET'])
@require_authentication()
def get_submission_detail(submission_id):
    """
    Get detailed submission information
    
    SRS Reference: M5.UC02 - View Submission Report (detailed view)
    """
    try:
        user_id = request.current_user.id
        
        detail_data, error = dashboard_service.get_submission_detail(submission_id, user_id)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 500
        
        return jsonify(detail_data)
        
    except Exception as e:
        current_app.logger.error(f"Submission detail error: {e}")
        return jsonify({'error': 'Error loading submission details'}), 500

@dashboard_bp.route('/deadlines', methods=['GET'])
@require_authentication()
def get_deadlines():
    """Get list of deadlines for the authenticated user"""
    try:
        user_id = request.current_user.id
        include_past = request.args.get('include_past', 'false').lower() == 'true'
        
        deadlines, error = dashboard_service.get_deadlines_list(user_id, include_past)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({'deadlines': deadlines})
        
    except Exception as e:
        current_app.logger.error(f"Deadlines list error: {e}")
        return jsonify({'error': 'Error loading deadlines'}), 500

@dashboard_bp.route('/deadlines', methods=['POST'])
@require_authentication()
def create_deadline():
    """Create a new deadline"""
    try:
        user_id = request.current_user.id
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('deadline_datetime'):
            return jsonify({'error': 'Title and deadline_datetime are required'}), 400
        
        deadline_data, error = dashboard_service.create_deadline(user_id, data)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Deadline created successfully',
            'deadline': deadline_data
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Deadline creation error: {e}")
        return jsonify({'error': 'Error creating deadline'}), 500

@dashboard_bp.route('/deadlines/<deadline_id>', methods=['PUT'])
@require_authentication()
def update_deadline(deadline_id):
    """Update an existing deadline"""
    try:
        user_id = request.current_user.id
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No update data provided'}), 400
        
        deadline_data, error = dashboard_service.update_deadline(deadline_id, user_id, data)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Deadline updated successfully',
            'deadline': deadline_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Deadline update error: {e}")
        return jsonify({'error': 'Error updating deadline'}), 500

@dashboard_bp.route('/deadlines/<deadline_id>', methods=['DELETE'])
@require_authentication()
def delete_deadline(deadline_id):
    """Delete a deadline"""
    try:
        user_id = request.current_user.id
        
        success, error = dashboard_service.delete_deadline(deadline_id, user_id)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Deadline deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Deadline deletion error: {e}")
        return jsonify({'error': 'Error deleting deadline'}), 500

@dashboard_bp.route('/submissions/<submission_id>', methods=['DELETE'])
@require_authentication()
def delete_submission(submission_id):
    """Delete a submission"""
    try:
        user_id = request.current_user.id
        
        success, error = dashboard_service.delete_submission(submission_id, user_id)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Submission deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Submission deletion error: {e}")
        return jsonify({'error': 'Error deleting submission'}), 500