"""
Module 3: Rule-Based AI Insights and Deadline Monitoring

Implements SRS requirements:
- M3.UC01: Evaluate Timeliness vs Deadline
- M3.UC02: Compute Contribution Change (Compare Snapshots)
- M3.UC03: Generate & Persist Heuristic Insights

Handles:
1. Reading metadata timestamps and comparing to deadlines
2. Detecting last-minute edits (< 1 hour before deadline)
3. Computing contribution growth based on version comparison
4. Classifying submissions as On-Time, Late, or Last-Minute Rush
5. Generating human-readable insight summaries
"""

from datetime import datetime, timedelta
import pytz
from flask import Blueprint, request, jsonify, current_app

from app.core.extensions import db
from app.models import (
    Submission, AnalysisResult, DocumentSnapshot, Deadline, 
    TimelinesssClassification, SubmissionStatus
)
from app.services.audit_service import AuditService
from app.services import InsightsService
from app.api.auth import get_auth_service
from app.schemas.dto import DeadlineDTO

insights_bp = Blueprint('insights', __name__)

# Initialize service
insights_service = InsightsService()

@insights_bp.route('/analyze/<submission_id>', methods=['POST'])
def analyze_insights(submission_id):
    """
    Generate heuristic insights for a submission
    
    Combines all three SRS use cases: M3.UC01, M3.UC02, M3.UC03
    """
    try:
        # Get submission
        submission = Submission.query.filter_by(id=submission_id).first()
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        # Check if analysis result exists
        if not submission.analysis_result:
            return jsonify({'error': 'Metadata analysis must be completed first'}), 400
        
        # Get deadline if specified
        deadline = None
        if submission.deadline_id:
            deadline = Deadline.query.filter_by(id=submission.deadline_id).first()
        
        # Generate insights
        insights, error = insights_service.generate_heuristic_insights(submission, deadline)
        
        if error:
            return jsonify({'error': error}), 500
        
        # Update analysis result with insights
        analysis_result = submission.analysis_result
        analysis_result.heuristic_insights = insights
        analysis_result.timeliness_classification = insights['timeliness']['classification']
        
        if insights['contribution_analysis']['has_comparison']:
            analysis_result.contribution_growth_percentage = insights['contribution_analysis']['change_percentage']
        
        db.session.commit()
        
        # Log insights generation
        AuditService.log_submission_event(
            'heuristic_insights_generated',
            submission,
            additional_metadata={
                'timeliness_classification': insights['timeliness']['classification'].value,
                'confidence_level': insights['overall_assessment']['confidence_level'],
                'flags_count': len(insights['overall_assessment']['flags'])
            }
        )
        
        return jsonify({
            'message': 'Heuristic insights generated successfully',
            'submission_id': submission_id,
            'insights': insights
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Insights analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@insights_bp.route('/timeliness/<submission_id>', methods=['GET'])
def get_timeliness_analysis(submission_id):
    """Get only timeliness analysis for a submission"""
    try:
        submission = Submission.query.filter_by(id=submission_id).first()
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        deadline = None
        if submission.deadline_id:
            deadline = Deadline.query.filter_by(id=submission.deadline_id).first()
        
        timeliness_result = insights_service.evaluate_submission_timeliness(submission, deadline)
        
        return jsonify({
            'submission_id': submission_id,
            'timeliness_analysis': timeliness_result,
            'deadline_info': DeadlineDTO.serialize(deadline) if deadline else None
        })
        
    except Exception as e:
        current_app.logger.error(f"Timeliness analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@insights_bp.route('/contribution/<submission_id>', methods=['GET'])
def get_contribution_analysis(submission_id):
    """Get only contribution growth analysis for a submission"""
    try:
        submission = Submission.query.filter_by(id=submission_id).first()
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        contribution_result = insights_service.compute_contribution_growth(submission)
        
        return jsonify({
            'submission_id': submission_id,
            'contribution_analysis': contribution_result
        })
        
    except Exception as e:
        current_app.logger.error(f"Contribution analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

