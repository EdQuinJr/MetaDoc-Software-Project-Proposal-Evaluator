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

from app import db
from app.models import (
    Submission, AnalysisResult, DocumentSnapshot, Deadline, 
    TimelinesssClassification, SubmissionStatus
)
from app.services.audit_service import AuditService

insights_bp = Blueprint('insights', __name__)

class HeuristicInsightsService:
    """Service for generating rule-based insights and deadline analysis"""
    
    def __init__(self):
        self.last_minute_threshold_hours = 1  # SRS: < 1 hour = last minute rush
        self.major_contribution_threshold = 50  # SRS: ≥50% = major contribution
    
    def evaluate_submission_timeliness(self, submission, deadline=None):
        """
        Evaluate timeliness of submission against deadline
        
        SRS Reference: M3.UC01 - Evaluate Timeliness of Submission
        """
        if not deadline:
            return {
                'classification': TimelinesssClassification.NO_DEADLINE,
                'message': 'No deadline set for this submission',
                'details': None
            }
        
        try:
            # Get submission timestamp (use last modified from metadata or submission time)
            submission_time = None
            
            if submission.analysis_result and submission.analysis_result.document_metadata:
                metadata = submission.analysis_result.document_metadata
                if metadata.get('last_modified_date'):
                    submission_time = datetime.fromisoformat(metadata['last_modified_date'].replace('Z', '+00:00'))
            
            # Fallback to submission creation time
            if not submission_time:
                submission_time = submission.created_at
            
            # Ensure timezone awareness
            if submission_time.tzinfo is None:
                submission_time = pytz.UTC.localize(submission_time)
            
            deadline_time = deadline.deadline_datetime
            if deadline_time.tzinfo is None:
                deadline_time = pytz.UTC.localize(deadline_time)
            
            # Calculate time difference
            time_difference = submission_time - deadline_time
            
            # Determine classification
            if time_difference <= timedelta(0):
                # Submitted before or at deadline
                time_before_deadline = abs(time_difference)
                
                if time_before_deadline <= timedelta(hours=self.last_minute_threshold_hours):
                    classification = TimelinesssClassification.LAST_MINUTE_RUSH
                    message = f"Last-minute submission (submitted {self._format_time_difference(time_before_deadline)} before deadline)"
                else:
                    classification = TimelinesssClassification.ON_TIME
                    message = f"On-time submission (submitted {self._format_time_difference(time_before_deadline)} before deadline)"
            else:
                # Submitted after deadline
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
        """
        Compute contribution growth between document versions
        
        SRS Reference: M3.UC02 - Compute Contribution Growth Between Versions
        """
        try:
            # Get current and previous snapshots
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
            
            # Look for previous snapshot with same file_id
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
            
            # Calculate percentage change
            word_count_change = current_snapshot.word_count - previous_snapshot.word_count
            
            if previous_snapshot.word_count > 0:
                change_percentage = (word_count_change / previous_snapshot.word_count) * 100
            else:
                change_percentage = 100 if current_snapshot.word_count > 0 else 0
            
            # Determine if major contribution (≥50% as per SRS)
            is_major_contribution = abs(change_percentage) >= self.major_contribution_threshold
            
            # Generate message
            if word_count_change > 0:
                if is_major_contribution:
                    message = f"Major content addition: +{word_count_change} words ({change_percentage:.1f}% increase)"
                else:
                    message = f"Content added: +{word_count_change} words ({change_percentage:.1f}% increase)"
            elif word_count_change < 0:
                if is_major_contribution:
                    message = f"Major content reduction: {word_count_change} words ({change_percentage:.1f}% decrease)"
                else:
                    message = f"Content reduced: {word_count_change} words ({change_percentage:.1f}% decrease)"
            else:
                message = "No significant word count change detected"
            
            return {
                'has_comparison': True,
                'message': message,
                'current_word_count': current_snapshot.word_count,
                'previous_word_count': previous_snapshot.word_count,
                'change_percentage': round(change_percentage, 2),
                'word_count_change': word_count_change,
                'is_major_contribution': is_major_contribution,
                'comparison_timespan': self._format_time_difference(
                    current_snapshot.created_at - previous_snapshot.created_at
                )
            }
            
        except Exception as e:
            current_app.logger.error(f"Contribution growth computation error: {e}")
            return {
                'has_comparison': False,
                'message': f'Error computing contribution growth: {e}',
                'current_word_count': 0,
                'previous_word_count': None,
                'change_percentage': None,
                'is_major_contribution': False
            }
    
    def detect_editing_patterns(self, submission):
        """Detect editing patterns and behaviors"""
        patterns = []
        
        try:
            if not submission.analysis_result or not submission.analysis_result.document_metadata:
                return {
                    'patterns_detected': [],
                    'message': 'Insufficient metadata for pattern analysis'
                }
            
            metadata = submission.analysis_result.document_metadata
            
            # Check revision count
            revision_count = metadata.get('revision_count', 0)
            if revision_count > 10:
                patterns.append({
                    'pattern': 'high_revision_count',
                    'description': f'High revision count detected ({revision_count} revisions)',
                    'implication': 'Document underwent extensive editing'
                })
            elif revision_count == 1 or revision_count == 0:
                patterns.append({
                    'pattern': 'minimal_revisions',
                    'description': f'Minimal revisions detected ({revision_count} revisions)',
                    'implication': 'Document may have been written in one session'
                })
            
            # Compare creation and modification dates
            created_date = metadata.get('creation_date')
            modified_date = metadata.get('last_modified_date')
            
            if created_date and modified_date:
                try:
                    created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    modified_dt = datetime.fromisoformat(modified_date.replace('Z', '+00:00'))
                    
                    time_span = modified_dt - created_dt
                    
                    if time_span <= timedelta(hours=2):
                        patterns.append({
                            'pattern': 'short_editing_window',
                            'description': f'Document created and finalized within {self._format_time_difference(time_span)}',
                            'implication': 'Concentrated writing session or minimal editing'
                        })
                    elif time_span >= timedelta(days=7):
                        patterns.append({
                            'pattern': 'extended_editing_period',
                            'description': f'Document edited over {self._format_time_difference(time_span)}',
                            'implication': 'Extended development and refinement process'
                        })
                        
                except Exception as e:
                    current_app.logger.warning(f"Date parsing error in pattern detection: {e}")
            
            return {
                'patterns_detected': patterns,
                'message': f'{len(patterns)} editing patterns identified' if patterns else 'No notable editing patterns detected'
            }
            
        except Exception as e:
            current_app.logger.error(f"Pattern detection error: {e}")
            return {
                'patterns_detected': [],
                'message': f'Error detecting patterns: {e}'
            }
    
    def generate_heuristic_insights(self, submission, deadline=None):
        """
        Generate comprehensive heuristic insights
        
        SRS Reference: M3.UC03 - Generate Heuristic Insights
        """
        insights = {}
        
        try:
            # Evaluate timeliness
            timeliness_result = self.evaluate_submission_timeliness(submission, deadline)
            insights['timeliness'] = timeliness_result
            
            # Compute contribution growth
            contribution_result = self.compute_contribution_growth(submission)
            insights['contribution_analysis'] = contribution_result
            
            # Detect editing patterns
            pattern_result = self.detect_editing_patterns(submission)
            insights['editing_patterns'] = pattern_result
            
            # Generate overall assessment
            assessment_flags = []
            risk_indicators = []
            
            # Timeliness assessment
            if timeliness_result['classification'] == TimelinesssClassification.LAST_MINUTE_RUSH:
                assessment_flags.append('last_minute_submission')
                risk_indicators.append('Potential rushed work due to last-minute submission')
            elif timeliness_result['classification'] == TimelinesssClassification.LATE:
                assessment_flags.append('late_submission')
                risk_indicators.append('Late submission may indicate time management issues')
            
            # Contribution assessment
            if contribution_result['is_major_contribution']:
                assessment_flags.append('major_changes')
                if contribution_result['change_percentage'] > 100:
                    risk_indicators.append('Substantial content changes may indicate significant revisions')
            
            # Content completeness assessment
            if submission.analysis_result:
                content_stats = submission.analysis_result.content_statistics or {}
                word_count = content_stats.get('word_count', 0)
                
                if word_count < current_app.config.get('MIN_DOCUMENT_WORDS', 50):
                    assessment_flags.append('incomplete_content')
                    risk_indicators.append('Document appears incomplete based on word count')
                
                if not submission.analysis_result.is_complete_document:
                    assessment_flags.append('validation_warnings')
                    risk_indicators.append('Document failed completeness validation')
            
            insights['overall_assessment'] = {
                'flags': assessment_flags,
                'risk_indicators': risk_indicators,
                'confidence_level': self._calculate_confidence_level(insights),
                'summary': self._generate_summary_message(insights, assessment_flags)
            }
            
            insights['analysis_timestamp'] = datetime.utcnow().isoformat()
            
            return insights, None
            
        except Exception as e:
            current_app.logger.error(f"Heuristic insights generation error: {e}")
            return None, f"Error generating insights: {e}"
    
    def _format_time_difference(self, time_delta):
        """Format time difference in human-readable format"""
        total_seconds = int(time_delta.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} seconds"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} minutes"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if minutes > 0:
                return f"{hours} hours, {minutes} minutes"
            else:
                return f"{hours} hours"
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            if hours > 0:
                return f"{days} days, {hours} hours"
            else:
                return f"{days} days"
    
    def _calculate_confidence_level(self, insights):
        """Calculate confidence level for insights based on available data"""
        confidence_factors = []
        
        # Timeliness confidence
        if insights['timeliness']['details']:
            confidence_factors.append('timeliness_data_available')
        
        # Contribution confidence
        if insights['contribution_analysis']['has_comparison']:
            confidence_factors.append('version_comparison_available')
        
        # Pattern confidence
        if insights['editing_patterns']['patterns_detected']:
            confidence_factors.append('editing_patterns_detected')
        
        confidence_score = len(confidence_factors) / 3  # Normalize to 0-1
        
        if confidence_score >= 0.8:
            return 'high'
        elif confidence_score >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_summary_message(self, insights, flags):
        """Generate overall summary message"""
        timeliness_class = insights['timeliness']['classification']
        
        if timeliness_class == TimelinesssClassification.ON_TIME:
            base_message = "Submission appears to be well-planned and timely"
        elif timeliness_class == TimelinesssClassification.LAST_MINUTE_RUSH:
            base_message = "Submission shows signs of last-minute preparation"
        elif timeliness_class == TimelinesssClassification.LATE:
            base_message = "Late submission detected"
        else:
            base_message = "Submission analyzed without deadline context"
        
        if 'major_changes' in flags:
            base_message += " with significant content development"
        
        if 'incomplete_content' in flags or 'validation_warnings' in flags:
            base_message += ", but content completeness issues were detected"
        
        return base_message

# Initialize service
insights_service = HeuristicInsightsService()

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
        
        if insights['contribution_analysis']['has comparison']:
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
            'deadline_info': deadline.to_dict() if deadline else None
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