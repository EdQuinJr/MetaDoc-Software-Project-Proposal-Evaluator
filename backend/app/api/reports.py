"""
Reports Module for MetaDoc

Implements SRS requirements:
- M5.UC03: Export Report (PDF / CSV)
- Report generation and export functionality
- Data formatting for professor dashboard
"""

import os
import csv
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import pandas as pd

from app.core.extensions import db
from app.models import Submission, AnalysisResult, User, Deadline, ReportExport
from app.services.audit_service import AuditService
from app.services import ReportService
from app.utils.decorators import require_authentication
from app.api.dashboard import dashboard_service

reports_bp = Blueprint('reports', __name__)

# Initialize service
report_service = None

def get_report_service():
    global report_service
    if report_service is None:
        from app.services import ReportService
        report_service = ReportService()
    return report_service

# Lazy initialize
report_service = get_report_service()

@reports_bp.route('/export/pdf', methods=['POST'])
@require_authentication()
def export_pdf_report():
    """
    Export submissions as PDF report
    
    SRS Reference: M5.UC03 - Export Report (PDF)
    """
    try:
        user = request.current_user
        data = request.get_json() or {}
        
        # Get submission IDs or use filters
        submission_ids = data.get('submission_ids', [])
        filters = data.get('filters', {})
        
        if submission_ids:
            # Export specific submissions
            submissions = Submission.query.filter(
                Submission.id.in_(submission_ids),
                Submission.professor_id == user.id
            ).all()
        else:
            # Export based on filters
            result = dashboard_service.get_submissions_list(
                user_id=user.id,
                filters=filters if filters else None
            )
            submission_data = result['submissions']
            submission_ids = [s['id'] for s in submission_data]
            
            submissions = Submission.query.filter(
                Submission.id.in_(submission_ids)
            ).all()
        
        if not submissions:
            return jsonify({'error': 'No submissions found to export'}), 400
        
        # Generate PDF
        filepath, error = get_report_service().generate_pdf_report(submissions, user, data)
        
        if error:
            return jsonify({'error': error}), 500
        
        # Create export record
        export_record = get_report_service().create_export_record(
            user_id=user.id,
            export_type='pdf',
            filepath=filepath,
            submission_ids=submission_ids,
            filter_params=filters
        )
        
        # Log export event
        AuditService.log_export_event('pdf', user.id, submission_ids, filters)
        
        return jsonify({
            'message': 'PDF report generated successfully',
            'export_id': export_record.id if export_record else None,
            'filename': os.path.basename(filepath),
            'submission_count': len(submissions)
        })
        
    except Exception as e:
        current_app.logger.error(f"PDF export error: {e}")
        return jsonify({'error': 'PDF export failed'}), 500

@reports_bp.route('/export/csv', methods=['POST'])
@require_authentication()
def export_csv_report():
    """
    Export submissions as CSV report
    
    SRS Reference: M5.UC03 - Export Report (CSV)
    """
    try:
        user = request.current_user
        data = request.get_json() or {}
        
        # Get submission IDs or use filters (same logic as PDF)
        submission_ids = data.get('submission_ids', [])
        filters = data.get('filters', {})
        
        if submission_ids:
            submissions = Submission.query.filter(
                Submission.id.in_(submission_ids),
                Submission.professor_id == user.id
            ).all()
        else:
            result = dashboard_service.get_submissions_list(
                user_id=user.id,
                filters=filters if filters else None
            )
            submission_data = result['submissions']
            submission_ids = [s['id'] for s in submission_data]
            
            submissions = Submission.query.filter(
                Submission.id.in_(submission_ids)
            ).all()
        
        if not submissions:
            return jsonify({'error': 'No submissions found to export'}), 400
        
        # Generate CSV
        filepath, error = get_report_service().generate_csv_report(submissions, user, data)
        
        if error:
            return jsonify({'error': error}), 500
        
        # Create export record
        export_record = get_report_service().create_export_record(
            user_id=user.id,
            export_type='csv',
            filepath=filepath,
            submission_ids=submission_ids,
            filter_params=filters
        )
        
        # Log export event
        AuditService.log_export_event('csv', user.id, submission_ids, filters)
        
        return jsonify({
            'message': 'CSV report generated successfully',
            'export_id': export_record.id if export_record else None,
            'filename': os.path.basename(filepath),
            'submission_count': len(submissions)
        })
        
    except Exception as e:
        current_app.logger.error(f"CSV export error: {e}")
        return jsonify({'error': 'CSV export failed'}), 500

@reports_bp.route('/download/<export_id>', methods=['GET'])
@require_authentication()
def download_report(export_id):
    """Download generated report file"""
    try:
        user = request.current_user
        
        # Find export record
        export_record = ReportExport.query.filter_by(
            id=export_id,
            user_id=user.id
        ).first()
        
        if not export_record:
            return jsonify({'error': 'Export not found or access denied'}), 404
        
        # Check if file exists
        if not os.path.exists(export_record.file_path):
            return jsonify({'error': 'Export file no longer available'}), 404
        
        # Check expiry
        if export_record.expires_at and export_record.expires_at < datetime.utcnow():
            return jsonify({'error': 'Export has expired'}), 410
        
        # Increment download count
        export_record.download_count += 1
        db.session.commit()
        
        # Log download event
        AuditService.log_event(
            'report_download',
            f'Report downloaded: {export_record.export_type.upper()}',
            user_id=user.id,
            metadata={
                'export_id': export_id,
                'export_type': export_record.export_type,
                'download_count': export_record.download_count
            }
        )
        
        return send_file(
            export_record.file_path,
            as_attachment=True,
            download_name=os.path.basename(export_record.file_path)
        )
        
    except Exception as e:
        current_app.logger.error(f"Report download error: {e}")
        return jsonify({'error': 'Download failed'}), 500

@reports_bp.route('/exports', methods=['GET'])
@require_authentication()
def get_export_history():
    """Get list of user's export history"""
    try:
        user = request.current_user
        
        exports = ReportExport.query.filter_by(user_id=user.id).order_by(
            desc(ReportExport.created_at)
        ).limit(50).all()
        
        export_data = []
        for export in exports:
            data = {
                'id': export.id,
                'export_type': export.export_type,
                'filename': os.path.basename(export.file_path),
                'file_size_mb': round(export.file_size / (1024*1024), 2),
                'created_at': export.created_at.isoformat(),
                'expires_at': export.expires_at.isoformat() if export.expires_at else None,
                'download_count': export.download_count,
                'submission_count': len(export.submissions_included) if export.submissions_included else 0,
                'is_expired': export.expires_at < datetime.utcnow() if export.expires_at else False,
                'is_available': os.path.exists(export.file_path)
            }
            export_data.append(data)
        
        return jsonify({
            'exports': export_data,
            'total_count': len(export_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Export history error: {e}")
        return jsonify({'error': 'Error loading export history'}), 500

