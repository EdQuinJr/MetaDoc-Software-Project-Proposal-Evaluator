"""
Report generation request/response schemas
"""

from typing import Optional

class ReportExportSchema:
    """Schema for report export request validation"""
    
    required_fields = ['export_type']
    optional_fields = ['deadline_id', 'status', 'date_from', 'date_to', 'student_id']
    
    @staticmethod
    def validate(data: dict) -> tuple[bool, Optional[str]]:
        """Validate report export request"""
        if not data:
            return False, "Request body is required"
        
        missing = [f for f in ReportExportSchema.required_fields if f not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        export_type = data.get('export_type', '').lower()
        if export_type not in ['pdf', 'csv']:
            return False, "export_type must be either 'pdf' or 'csv'"
        
        # Validate status if provided
        if 'status' in data:
            valid_statuses = ['pending', 'processing', 'completed', 'failed', 'warning']
            if data['status'] not in valid_statuses:
                return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
        return True, None
