"""
Report Service - Handles report generation and export

Extracted from api/reports.py to follow proper service layer architecture.
"""

import os
import csv
import io
from datetime import datetime
from flask import current_app
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import pandas as pd

from app.core.extensions import db
from app.models import Submission, AnalysisResult, ReportExport


class ReportService:
    """Service for generating and exporting reports in various formats"""
    
    def __init__(self):
        pass
    
    @property
    def reports_dir(self):
        """Get reports directory from config (lazy load)"""
        reports_path = current_app.config.get('REPORTS_STORAGE_PATH', './reports')
        if not os.path.exists(reports_path):
            os.makedirs(reports_path, exist_ok=True)
        return reports_path
    
    def generate_pdf_report(self, submissions, user, export_params=None):
        """Generate comprehensive PDF report"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"metadoc_report_{timestamp}.pdf"
            filepath = os.path.join(self.reports_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#8B0000'),
                spaceAfter=30
            )
            
            title = Paragraph("MetaDoc Submission Report", title_style)
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            info_data = [
                ['Report Generated:', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')],
                ['Professor:', user.name],
                ['Email:', user.email],
                ['Total Submissions:', str(len(submissions))]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))
            
            submissions_header = Paragraph("Submissions Summary", styles['Heading2'])
            story.append(submissions_header)
            story.append(Spacer(1, 0.1*inch))
            
            table_data = [['#', 'Student', 'File', 'Status', 'Word Count', 'Submitted']]
            
            for idx, submission in enumerate(submissions, 1):
                word_count = 'N/A'
                if submission.analysis_result and submission.analysis_result.content_statistics:
                    word_count = str(submission.analysis_result.content_statistics.get('word_count', 'N/A'))
                
                table_data.append([
                    str(idx),
                    submission.student_name or 'Unknown',
                    submission.original_filename[:30] + '...' if len(submission.original_filename) > 30 else submission.original_filename,
                    submission.status.value,
                    word_count,
                    submission.created_at.strftime('%Y-%m-%d')
                ])
            
            submissions_table = Table(table_data, colWidths=[0.5*inch, 1.5*inch, 2*inch, 1*inch, 1*inch, 1*inch])
            submissions_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(submissions_table)
            
            doc.build(story)
            
            file_size = os.path.getsize(filepath)
            
            return {
                'filename': filename,
                'filepath': filepath,
                'file_size': file_size
            }, None
            
        except Exception as e:
            current_app.logger.error(f"PDF generation failed: {e}")
            return None, str(e)
    
    def generate_csv_report(self, submissions, user, export_params=None):
        """Generate CSV report"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"metadoc_report_{timestamp}.csv"
            filepath = os.path.join(self.reports_dir, filename)
            
            data = []
            for submission in submissions:
                row = {
                    'Submission ID': submission.job_id,
                    'Student Name': submission.student_name or 'Unknown',
                    'Student ID': submission.student_id or 'N/A',
                    'File Name': submission.original_filename,
                    'Status': submission.status.value,
                    'Submission Type': submission.submission_type,
                    'Submitted At': submission.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'File Size (MB)': round(submission.file_size / (1024 * 1024), 2)
                }
                
                if submission.analysis_result:
                    analysis = submission.analysis_result
                    if analysis.content_statistics:
                        row['Word Count'] = analysis.content_statistics.get('word_count', 'N/A')
                        row['Page Count'] = analysis.content_statistics.get('estimated_pages', 'N/A')
                    
                    row['Readability Score'] = analysis.flesch_kincaid_score or 'N/A'
                    row['Timeliness'] = analysis.timeliness_classification.value if analysis.timeliness_classification else 'N/A'
                else:
                    row['Word Count'] = 'N/A'
                    row['Page Count'] = 'N/A'
                    row['Readability Score'] = 'N/A'
                    row['Timeliness'] = 'N/A'
                
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            
            file_size = os.path.getsize(filepath)
            
            return {
                'filename': filename,
                'filepath': filepath,
                'file_size': file_size
            }, None
            
        except Exception as e:
            current_app.logger.error(f"CSV generation failed: {e}")
            return None, str(e)
    
    def create_export_record(self, user_id, export_type, file_info, filter_params, submission_ids):
        """Create export record in database"""
        try:
            export_record = ReportExport(
                export_type=export_type,
                file_path=file_info['filepath'],
                file_size=file_info['file_size'],
                filter_parameters=filter_params,
                submissions_included=submission_ids,
                user_id=user_id,
                expires_at=datetime.utcnow() + pd.Timedelta(days=7)
            )
            
            db.session.add(export_record)
            db.session.commit()
            
            return export_record, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Export record creation failed: {e}")
            return None, str(e)
    
    def get_export_record(self, export_id, user_id):
        """Get export record by ID"""
        try:
            export_record = ReportExport.query.filter_by(
                id=export_id,
                user_id=user_id
            ).first()
            
            if not export_record:
                return None, "Export not found"
            
            if export_record.expires_at < datetime.utcnow():
                return None, "Export has expired"
            
            return export_record, None
            
        except Exception as e:
            current_app.logger.error(f"Export record retrieval failed: {e}")
            return None, str(e)
    
    def get_user_exports(self, user_id):
        """Get all exports for a user"""
        try:
            exports = ReportExport.query.filter_by(
                user_id=user_id
            ).order_by(ReportExport.created_at.desc()).all()
            
            return exports, None
            
        except Exception as e:
            current_app.logger.error(f"User exports retrieval failed: {e}")
            return None, str(e)
    
    def increment_download_count(self, export_id):
        """Increment download count for an export"""
        try:
            export_record = ReportExport.query.filter_by(id=export_id).first()
            if export_record:
                export_record.download_count += 1
                db.session.commit()
            return True, None
        except Exception as e:
            current_app.logger.error(f"Download count increment failed: {e}")
            return False, str(e)
