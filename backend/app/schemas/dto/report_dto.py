"""
Report-related Data Transfer Objects
"""

from typing import Optional, Dict, Any, List


class ReportExportDTO:
    """DTO for Report Export serialization"""
    
    @staticmethod
    def serialize(report_export) -> Dict[str, Any]:
        """Serialize ReportExport model to dictionary"""
        if not report_export:
            return None
        
        return {
            'id': report_export.id,
            'export_type': report_export.export_type,
            'file_path': report_export.file_path,
            'file_size': report_export.file_size,
            'filter_parameters': report_export.filter_parameters,
            'submissions_included': report_export.submissions_included,
            'user_id': report_export.user_id,
            'download_count': report_export.download_count,
            'expires_at': report_export.expires_at.isoformat() if report_export.expires_at else None,
            'created_at': report_export.created_at.isoformat() if hasattr(report_export, 'created_at') else None
        }
    
    @staticmethod
    def serialize_list(report_exports) -> List[Dict[str, Any]]:
        """Serialize list of ReportExport models"""
        return [ReportExportDTO.serialize(report) for report in report_exports]
    
    @staticmethod
    def serialize_minimal(report_export) -> Dict[str, Any]:
        """Serialize report export with minimal information for list view"""
        if not report_export:
            return None
        
        return {
            'id': report_export.id,
            'export_type': report_export.export_type,
            'file_size': report_export.file_size,
            'download_count': report_export.download_count,
            'created_at': report_export.created_at.isoformat() if hasattr(report_export, 'created_at') else None,
            'expires_at': report_export.expires_at.isoformat() if report_export.expires_at else None
        }
