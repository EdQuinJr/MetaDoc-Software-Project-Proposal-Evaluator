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

from app import db
from app.models import Submission, AnalysisResult, User, Deadline, ReportExport
from app.services.audit_service import AuditService
from app.modules.dashboard import dashboard_service, require_authentication

reports_bp = Blueprint('reports', __name__)

class ReportGenerationService:
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
            # Create filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"metadoc_report_{timestamp}.pdf"
            filepath = os.path.join(self.reports_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.HexColor('#2c3e50')
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=20,
                textColor=colors.HexColor('#34495e')
            )
            
            # Title and header
            story.append(Paragraph("MetaDoc Analysis Report", title_style))
            story.append(Paragraph(f"Generated on: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}", styles['Normal']))
            story.append(Paragraph(f"Professor: {user.name} ({user.email})", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", subtitle_style))
            
            total_submissions = len(submissions)
            completed_analyses = len([s for s in submissions if s.analysis_result])
            
            # Calculate summary statistics
            summary_stats = self._calculate_summary_statistics(submissions)
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Submissions', str(total_submissions)],
                ['Completed Analyses', str(completed_analyses)],
                ['Average Word Count', f"{summary_stats['avg_word_count']:.0f}"],
                ['Average Readability Grade', f"{summary_stats['avg_readability']:.1f}"],
                ['On-Time Submissions', f"{summary_stats['on_time_count']} ({summary_stats['on_time_percent']:.1f}%)"],
                ['Late Submissions', f"{summary_stats['late_count']} ({summary_stats['late_percent']:.1f}%)"],
                ['Last-Minute Rush', f"{summary_stats['rush_count']} ({summary_stats['rush_percent']:.1f}%)"]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Detailed Submissions
            story.append(Paragraph("Detailed Submission Analysis", subtitle_style))
            
            for i, submission in enumerate(submissions):
                if i > 0:
                    story.append(Spacer(1, 15))
                
                # Submission header
                submission_title = f"Submission {i+1}: {submission.original_filename}"
                story.append(Paragraph(submission_title, styles['Heading3']))
                
                # Basic information
                basic_info = [
                    ['Field', 'Value'],
                    ['Student Name', submission.student_name or 'Not provided'],
                    ['Student Email', submission.student_email or 'Not provided'],
                    ['Submission Type', submission.submission_type.title()],
                    ['File Size', f"{submission.file_size / (1024*1024):.2f} MB"],
                    ['Submitted On', submission.created_at.strftime('%Y-%m-%d %H:%M UTC')],
                    ['Status', submission.status.value.title()]
                ]
                
                basic_table = Table(basic_info, colWidths=[2*inch, 3*inch])
                basic_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#95a5a6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(basic_table)
                story.append(Spacer(1, 10))
                
                # Analysis results
                if submission.analysis_result:
                    analysis = submission.analysis_result
                    
                    # Content Statistics
                    if analysis.content_statistics:
                        stats = analysis.content_statistics
                        content_data = [
                            ['Content Metric', 'Value'],
                            ['Word Count', str(stats.get('word_count', 'N/A'))],
                            ['Sentence Count', str(stats.get('sentence_count', 'N/A'))],
                            ['Paragraph Count', str(stats.get('paragraph_count', 'N/A'))],
                            ['Estimated Pages', str(stats.get('estimated_pages', 'N/A'))],
                            ['Avg Words/Sentence', f"{stats.get('average_words_per_sentence', 0):.1f}"]
                        ]
                        
                        content_table = Table(content_data, colWidths=[2*inch, 1.5*inch])
                        content_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        story.append(Paragraph("Content Analysis:", styles['Heading4']))
                        story.append(content_table)
                        story.append(Spacer(1, 10))
                    
                    # Readability and NLP
                    readability_data = [
                        ['Analysis Type', 'Result'],
                        ['Flesch-Kincaid Grade', f"{analysis.flesch_kincaid_score:.1f}" if analysis.flesch_kincaid_score else 'N/A'],
                        ['Reading Level', analysis.readability_grade or 'N/A'],
                        ['Timeliness Classification', analysis.timeliness_classification.value.replace('_', ' ').title() if analysis.timeliness_classification else 'N/A'],
                        ['Document Complete', 'Yes' if analysis.is_complete_document else 'No'],
                        ['Validation Warnings', str(len(analysis.validation_warnings)) if analysis.validation_warnings else '0']
                    ]
                    
                    readability_table = Table(readability_data, colWidths=[2*inch, 2*inch])
                    readability_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    story.append(Paragraph("Readability & Quality Analysis:", styles['Heading4']))
                    story.append(readability_table)
                    
                    # Insights and recommendations
                    if analysis.heuristic_insights:
                        insights = analysis.heuristic_insights
                        
                        if insights.get('overall_assessment', {}).get('summary'):
                            story.append(Spacer(1, 10))
                            story.append(Paragraph("Key Insights:", styles['Heading4']))
                            story.append(Paragraph(insights['overall_assessment']['summary'], styles['Normal']))
                        
                        # Risk indicators
                        risk_indicators = insights.get('overall_assessment', {}).get('risk_indicators', [])
                        if risk_indicators:
                            story.append(Spacer(1, 5))
                            story.append(Paragraph("Risk Indicators:", styles['Heading4']))
                            for indicator in risk_indicators:
                                story.append(Paragraph(f"• {indicator}", styles['Normal']))
                
                else:
                    story.append(Paragraph("Analysis not completed", styles['Normal']))
                
                # Add page break between submissions (except last one)
                if i < len(submissions) - 1:
                    story.append(Spacer(1, 20))
            
            # Generate PDF
            doc.build(story)
            
            return filepath, None
            
        except Exception as e:
            current_app.logger.error(f"PDF generation failed: {e}")
            return None, f"PDF generation error: {e}"
    
    def generate_csv_report(self, submissions, user, export_params=None):
        """Generate CSV report with submission data"""
        try:
            # Create filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"metadoc_report_{timestamp}.csv"
            filepath = os.path.join(self.reports_dir, filename)
            
            # Prepare data
            csv_data = []
            
            for submission in submissions:
                row = {
                    'Submission ID': submission.job_id,
                    'Filename': submission.original_filename,
                    'Student Name': submission.student_name or '',
                    'Student Email': submission.student_email or '',
                    'Submission Type': submission.submission_type,
                    'File Size (MB)': round(submission.file_size / (1024*1024), 2),
                    'Submitted On': submission.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Status': submission.status.value
                }
                
                if submission.analysis_result:
                    analysis = submission.analysis_result
                    
                    # Content statistics
                    if analysis.content_statistics:
                        stats = analysis.content_statistics
                        row.update({
                            'Word Count': stats.get('word_count', ''),
                            'Sentence Count': stats.get('sentence_count', ''),
                            'Paragraph Count': stats.get('paragraph_count', ''),
                            'Estimated Pages': stats.get('estimated_pages', ''),
                            'Avg Words per Sentence': stats.get('average_words_per_sentence', '')
                        })
                    
                    # Readability and analysis
                    row.update({
                        'Flesch-Kincaid Grade': analysis.flesch_kincaid_score or '',
                        'Reading Level': analysis.readability_grade or '',
                        'Timeliness Classification': analysis.timeliness_classification.value if analysis.timeliness_classification else '',
                        'Contribution Growth %': analysis.contribution_growth_percentage or '',
                        'Document Complete': 'Yes' if analysis.is_complete_document else 'No',
                        'Validation Warnings': len(analysis.validation_warnings) if analysis.validation_warnings else 0,
                        'Processing Duration (seconds)': analysis.processing_duration_seconds or ''
                    })
                    
                    # Named entities count
                    if analysis.named_entities and analysis.named_entities.get('entity_counts'):
                        entity_counts = analysis.named_entities['entity_counts']
                        row.update({
                            'Named Entities - People': entity_counts.get('PERSON', 0),
                            'Named Entities - Organizations': entity_counts.get('ORG', 0),
                            'Named Entities - Dates': entity_counts.get('DATE', 0),
                            'Named Entities - Total': analysis.named_entities.get('total_entities', 0)
                        })
                    
                    # AI insights
                    if analysis.ai_summary:
                        row['AI Summary'] = analysis.ai_summary
                else:
                    # Fill empty values for submissions without analysis
                    analysis_fields = [
                        'Word Count', 'Sentence Count', 'Paragraph Count', 'Estimated Pages',
                        'Avg Words per Sentence', 'Flesch-Kincaid Grade', 'Reading Level',
                        'Timeliness Classification', 'Contribution Growth %', 'Document Complete',
                        'Validation Warnings', 'Processing Duration (seconds)',
                        'Named Entities - People', 'Named Entities - Organizations',
                        'Named Entities - Dates', 'Named Entities - Total', 'AI Summary'
                    ]
                    for field in analysis_fields:
                        row[field] = ''
                
                csv_data.append(row)
            
            # Write CSV file
            if csv_data:
                fieldnames = csv_data[0].keys()
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(csv_data)
            
            return filepath, None
            
        except Exception as e:
            current_app.logger.error(f"CSV generation failed: {e}")
            return None, f"CSV generation error: {e}"
    
    def _calculate_summary_statistics(self, submissions):
        """Calculate summary statistics for report"""
        try:
            stats = {
                'avg_word_count': 0,
                'avg_readability': 0,
                'on_time_count': 0,
                'late_count': 0,
                'rush_count': 0,
                'on_time_percent': 0,
                'late_percent': 0,
                'rush_percent': 0
            }
            
            analyzed_submissions = [s for s in submissions if s.analysis_result]
            
            if analyzed_submissions:
                # Word count average
                word_counts = []
                readability_scores = []
                timeliness_counts = {'on_time': 0, 'late': 0, 'rush': 0}
                
                for submission in analyzed_submissions:
                    analysis = submission.analysis_result
                    
                    # Word count
                    if analysis.content_statistics:
                        word_count = analysis.content_statistics.get('word_count')
                        if word_count:
                            word_counts.append(word_count)
                    
                    # Readability
                    if analysis.flesch_kincaid_score:
                        readability_scores.append(analysis.flesch_kincaid_score)
                    
                    # Timeliness
                    if analysis.timeliness_classification:
                        if analysis.timeliness_classification.value == 'on_time':
                            timeliness_counts['on_time'] += 1
                        elif analysis.timeliness_classification.value == 'late':
                            timeliness_counts['late'] += 1
                        elif analysis.timeliness_classification.value == 'last_minute_rush':
                            timeliness_counts['rush'] += 1
                
                # Calculate averages
                if word_counts:
                    stats['avg_word_count'] = sum(word_counts) / len(word_counts)
                
                if readability_scores:
                    stats['avg_readability'] = sum(readability_scores) / len(readability_scores)
                
                # Timeliness statistics
                total_timeliness = sum(timeliness_counts.values())
                if total_timeliness > 0:
                    stats['on_time_count'] = timeliness_counts['on_time']
                    stats['late_count'] = timeliness_counts['late']
                    stats['rush_count'] = timeliness_counts['rush']
                    stats['on_time_percent'] = (timeliness_counts['on_time'] / total_timeliness) * 100
                    stats['late_percent'] = (timeliness_counts['late'] / total_timeliness) * 100
                    stats['rush_percent'] = (timeliness_counts['rush'] / total_timeliness) * 100
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Statistics calculation failed: {e}")
            return {
                'avg_word_count': 0, 'avg_readability': 0,
                'on_time_count': 0, 'late_count': 0, 'rush_count': 0,
                'on_time_percent': 0, 'late_percent': 0, 'rush_percent': 0
            }
    
    def create_export_record(self, user_id, export_type, filepath, submission_ids, filter_params=None):
        """Create export record in database"""
        try:
            file_size = os.path.getsize(filepath)
            
            export_record = ReportExport(
                export_type=export_type,
                file_path=filepath,
                file_size=file_size,
                user_id=user_id,
                submissions_included=submission_ids,
                filter_parameters=filter_params,
                expires_at=datetime.utcnow() + timedelta(days=7)  # Expire after 7 days
            )
            
            db.session.add(export_record)
            db.session.commit()
            
            return export_record
            
        except Exception as e:
            current_app.logger.error(f"Export record creation failed: {e}")
            return None

# Initialize service lazily
report_service = None

def get_report_service():
    """Get or create the report service instance"""
    global report_service
    if report_service is None:
        report_service = ReportGenerationService()
    return report_service

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