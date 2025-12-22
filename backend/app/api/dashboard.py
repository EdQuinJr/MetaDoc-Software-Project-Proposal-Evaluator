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

from app.core.extensions import db
from app.models import (
    Submission, AnalysisResult, Deadline, User, DocumentSnapshot, AuditLog,
    SubmissionStatus, TimelinesssClassification
)
from app.services.audit_service import AuditService
from app.services import DashboardService
from app.api.auth import get_auth_service
from app.utils.decorators import require_authentication
from app.schemas.dto import (
    SubmissionListDTO, SubmissionDetailDTO, DeadlineDTO, DeadlineListDTO
)

dashboard_bp = Blueprint('dashboard', __name__)

# Initialize service
dashboard_service = None

def get_dashboard_service():
    global dashboard_service
    if dashboard_service is None:
        from app.services import DashboardService
        dashboard_service = DashboardService()
    return dashboard_service

# Lazy initialize
dashboard_service = get_dashboard_service()

@dashboard_bp.route('/overview', methods=['GET'])
@require_authentication()
def get_dashboard_overview():
    """
    Get dashboard overview with statistics
    
    SRS Reference: Dashboard functionality for professor interface
    """
    try:
        user_id = request.current_user.id
        
        overview_data, error = dashboard_service.get_dashboard_overview(user_id)
        
        if error:
            return jsonify({'error': error}), 500
        
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
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        result, error = dashboard_service.get_submissions_list(
            user_id=user_id,
            filters=filters if filters else None,
            page=page,
            per_page=per_page
        )
        
        if error:
            return jsonify({'error': error}), 500
        
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
        
        submission, error = dashboard_service.get_submission_detail(submission_id, user_id)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 500
        
        # Serialize submission using DTO
        from app.schemas.dto import SubmissionDetailDTO
        return jsonify(SubmissionDetailDTO.serialize(submission))
        
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
        
        deadlines, error = dashboard_service.get_deadlines_list(user_id)
        
        if error:
            return jsonify({'error': error}), 500
        
        # Serialize deadlines using DTO
        from app.schemas.dto import DeadlineListDTO
        return jsonify({
            'deadlines': [DeadlineListDTO.serialize(d) for d in deadlines]
        })
        
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
        
        deadline, error = dashboard_service.create_deadline(user_id, data)
        
        if error:
            return jsonify({'error': error}), 400
        
        from app.schemas.dto import DeadlineDTO
        return jsonify({
            'message': 'Deadline created successfully',
            'deadline': DeadlineDTO.serialize(deadline)
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
        
        deadline, error = dashboard_service.update_deadline(deadline_id, user_id, data)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 400
        
        from app.schemas.dto import DeadlineDTO
        return jsonify({
            'message': 'Deadline updated successfully',
            'deadline': DeadlineDTO.serialize(deadline)
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

