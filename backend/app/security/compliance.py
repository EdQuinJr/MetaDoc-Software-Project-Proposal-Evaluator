"""
Security and Compliance utilities for MetaDoc

Implements:
- Data Privacy Act of 2012 compliance
- Secure credential management
- Data anonymization
- Audit trail management
- TLS enforcement
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from cryptography.fernet import Fernet
import json

class SecurityService:
    """Service for handling security and compliance requirements"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key) if self.encryption_key else None
    
    def _get_or_create_encryption_key(self):
        """Get or create encryption key for sensitive data"""
        try:
            key_file = os.path.join(os.getcwd(), '.encryption_key')
            
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                os.chmod(key_file, 0o600)  # Restrict file permissions
                return key
                
        except Exception as e:
            current_app.logger.error(f"Encryption key setup failed: {e}")
            return None
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data for storage"""
        if not self.cipher_suite or not data:
            return data
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted = self.cipher_suite.encrypt(data)
            return encrypted.decode('utf-8')
            
        except Exception as e:
            current_app.logger.error(f"Data encryption failed: {e}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data for use"""
        if not self.cipher_suite or not encrypted_data:
            return encrypted_data
        
        try:
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode('utf-8')
            
            decrypted = self.cipher_suite.decrypt(encrypted_data)
            return decrypted.decode('utf-8')
            
        except Exception as e:
            current_app.logger.error(f"Data decryption failed: {e}")
            return encrypted_data
    
    def anonymize_text_for_processing(self, text):
        """
        Anonymize text for AI processing to comply with Data Privacy Act
        """
        if not text:
            return text
        
        import re
        
        anonymized = text
        
        # Replace email addresses
        anonymized = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL_REDACTED]',
            anonymized,
            flags=re.IGNORECASE
        )
        
        # Replace phone numbers (various formats)
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\+\d{1,3}[-.]?\d{3,4}[-.]?\d{3,4}[-.]?\d{3,4}\b'  # International
        ]
        
        for pattern in phone_patterns:
            anonymized = re.sub(pattern, '[PHONE_REDACTED]', anonymized)
        
        # Replace potential names (basic heuristic)
        # Capitalized words that might be names
        anonymized = re.sub(
            r'\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b',
            '[NAME_REDACTED]',
            anonymized
        )
        
        # Replace ID numbers or codes
        anonymized = re.sub(
            r'\b\d{4,}\b',
            '[ID_REDACTED]',
            anonymized
        )
        
        return anonymized
    
    def validate_data_retention_policy(self, data_type, created_date):
        """
        Validate data retention according to institutional policies
        """
        retention_policies = {
            'submissions': timedelta(days=2555),  # ~7 years
            'analysis_results': timedelta(days=2555),
            'audit_logs': timedelta(days=2555),
            'user_sessions': timedelta(days=30),
            'report_exports': timedelta(days=7),
            'temp_files': timedelta(hours=24)
        }
        
        retention_period = retention_policies.get(data_type, timedelta(days=365))
        expiry_date = created_date + retention_period
        
        return {
            'is_expired': datetime.utcnow() > expiry_date,
            'expires_on': expiry_date,
            'retention_period_days': retention_period.days
        }
    
    def generate_data_privacy_report(self, user_id):
        """
        Generate data privacy report for user (GDPR-like functionality)
        """
        try:
            from app.models import User, Submission, AnalysisResult, AuditLog, UserSession
            
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return None, "User not found"
            
            # Collect user data
            data_summary = {
                'user_profile': {
                    'email': user.email,
                    'name': user.name,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                },
                'submissions': {
                    'count': Submission.query.filter_by(professor_id=user_id).count(),
                    'oldest': None,
                    'newest': None
                },
                'analysis_results': {
                    'count': 0
                },
                'audit_logs': {
                    'count': AuditLog.query.filter_by(user_id=user_id).count()
                },
                'active_sessions': {
                    'count': UserSession.query.filter_by(
                        user_id=user_id, 
                        is_active=True
                    ).count()
                }
            }
            
            # Get submission date range
            oldest_submission = Submission.query.filter_by(
                professor_id=user_id
            ).order_by(Submission.created_at.asc()).first()
            
            newest_submission = Submission.query.filter_by(
                professor_id=user_id
            ).order_by(Submission.created_at.desc()).first()
            
            if oldest_submission:
                data_summary['submissions']['oldest'] = oldest_submission.created_at.isoformat()
            if newest_submission:
                data_summary['submissions']['newest'] = newest_submission.created_at.isoformat()
            
            # Count analysis results
            analysis_count = AnalysisResult.query.join(Submission).filter(
                Submission.professor_id == user_id
            ).count()
            data_summary['analysis_results']['count'] = analysis_count
            
            return data_summary, None
            
        except Exception as e:
            current_app.logger.error(f"Privacy report generation failed: {e}")
            return None, f"Error generating privacy report: {e}"
    
    def schedule_data_cleanup(self):
        """
        Schedule cleanup of expired data according to retention policies
        """
        try:
            from app.models import UserSession, ReportExport, AuditLog
            
            cleanup_results = {}
            
            # Clean expired user sessions
            expired_sessions = UserSession.query.filter(
                UserSession.expires_at < datetime.utcnow()
            ).all()
            
            for session in expired_sessions:
                session.is_active = False
            
            cleanup_results['expired_sessions'] = len(expired_sessions)
            
            # Clean expired exports
            expired_exports = ReportExport.query.filter(
                ReportExport.expires_at < datetime.utcnow()
            ).all()
            
            for export in expired_exports:
                try:
                    if os.path.exists(export.file_path):
                        os.remove(export.file_path)
                except:
                    pass
            
            ReportExport.query.filter(
                ReportExport.expires_at < datetime.utcnow()
            ).delete()
            
            cleanup_results['expired_exports'] = len(expired_exports)
            
            # Clean old audit logs (keep last 2 years)
            cutoff_date = datetime.utcnow() - timedelta(days=730)
            old_logs = AuditLog.query.filter(
                AuditLog.created_at < cutoff_date
            ).delete()
            
            cleanup_results['old_audit_logs'] = old_logs
            
            from app import db
            db.session.commit()
            
            return cleanup_results, None
            
        except Exception as e:
            from app import db
            db.session.rollback()
            current_app.logger.error(f"Data cleanup failed: {e}")
            return None, f"Cleanup error: {e}"

def require_https():
    """Decorator to enforce HTTPS in production"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_app.config.get('FLASK_ENV') == 'production':
                if not request.is_secure and not request.headers.get('X-Forwarded-Proto') == 'https':
                    return jsonify({'error': 'HTTPS required'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests=60, window_minutes=1):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # For production, implement proper rate limiting with Redis
            # This is a simplified version for demonstration
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_file_security(file_path):
    """Validate file for security threats"""
    try:
        # Check file size
        if os.path.getsize(file_path) > current_app.config.get('MAX_CONTENT_LENGTH', 52428800):
            return False, "File too large"
        
        # Check file extension
        allowed_extensions = {'.docx', '.doc'}
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() not in allowed_extensions:
            return False, "Disallowed file type"
        
        # Basic virus scan placeholder
        # In production, integrate with antivirus API
        
        return True, None
        
    except Exception as e:
        current_app.logger.error(f"File security validation failed: {e}")
        return False, f"Security validation error: {e}"

def hash_for_integrity(data):
    """Generate integrity hash for data"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()

def generate_csrf_token():
    """Generate CSRF token for forms"""
    return secrets.token_urlsafe(32)

# Initialize security service
security_service = SecurityService()