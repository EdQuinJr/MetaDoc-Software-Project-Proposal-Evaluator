"""
Application-wide constants for MetaDoc

Centralizes all constant values used throughout the application
for better maintainability and consistency.
"""

# File Upload Constants
ALLOWED_EXTENSIONS = {'docx', 'doc'}
ALLOWED_MIME_TYPES = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'application/vnd.google-apps.document',
    'application/zip'  # DOCX files are ZIP archives
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
UPLOAD_FOLDER = './uploads'
TEMP_STORAGE_PATH = './temp_files'

# Submission Status
class SubmissionStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    WARNING = "warning"

# Timeliness Classification
class TimelinesssClassification:
    ON_TIME = "on_time"
    LATE = "late"
    LAST_MINUTE_RUSH = "last_minute_rush"
    NO_DEADLINE = "no_deadline"

# User Roles
class UserRole:
    PROFESSOR = "professor"
    ADMIN = "admin"
    STUDENT = "student"

# Session & Token Constants
SESSION_TIMEOUT = 3600  # 1 hour in seconds
SUBMISSION_TOKEN_VALIDITY = 30  # days
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour

# NLP Constants
DEFAULT_LANGUAGE = 'en'
MAX_DOCUMENT_WORDS = 15000
MIN_DOCUMENT_WORDS = 50

# Report Constants
REPORT_FORMATS = ['pdf', 'csv']
REPORTS_STORAGE_PATH = './reports'

# Audit Event Types
class AuditEventType:
    USER_LOGIN = 'user_login'
    USER_LOGOUT = 'user_logout'
    SUBMISSION_CREATED = 'submission_created'
    SUBMISSION_DELETED = 'submission_deleted'
    DEADLINE_CREATED = 'deadline_created'
    DEADLINE_UPDATED = 'deadline_updated'
    DEADLINE_DELETED = 'deadline_deleted'
    ANALYSIS_STARTED = 'analysis_started'
    ANALYSIS_COMPLETED = 'analysis_completed'
    REPORT_GENERATED = 'report_generated'
    DATA_ACCESSED = 'data_accessed'

# Google Drive Constants
GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
GOOGLE_OAUTH_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

# Pagination Constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Validation Patterns
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
GOOGLE_DRIVE_URL_PATTERNS = [
    r'https://drive\.google\.com/file/d/([a-zA-Z0-9-_]+)',
    r'https://docs\.google\.com/document/d/([a-zA-Z0-9-_]+)',
    r'https://drive\.google\.com/open\?id=([a-zA-Z0-9-_]+)'
]

# Error Messages
ERROR_MESSAGES = {
    'auth_required': 'Authentication required',
    'invalid_credentials': 'Invalid credentials',
    'access_denied': 'Access denied',
    'resource_not_found': 'Resource not found',
    'invalid_file_type': 'Invalid file type. Only DOCX and DOC files are allowed',
    'file_too_large': 'File size exceeds maximum limit',
    'duplicate_submission': 'This file has already been submitted',
    'invalid_deadline': 'Invalid deadline or access denied',
    'deadline_expired': 'The deadline has passed',
    'token_expired': 'Token has expired',
    'invalid_token': 'Invalid token',
}

# Success Messages
SUCCESS_MESSAGES = {
    'login_success': 'Login successful',
    'logout_success': 'Logout successful',
    'submission_created': 'Submission created successfully',
    'submission_deleted': 'Submission deleted successfully',
    'deadline_created': 'Deadline created successfully',
    'deadline_updated': 'Deadline updated successfully',
    'deadline_deleted': 'Deadline deleted successfully',
    'analysis_started': 'Analysis started',
    'report_generated': 'Report generated successfully',
}
