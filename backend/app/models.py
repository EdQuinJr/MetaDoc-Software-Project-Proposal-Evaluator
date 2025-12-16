"""
Database models for MetaDoc system

Following the SRS specifications for:
- Submission tracking
- Metadata storage
- Analysis results
- User management
- Audit logging
"""

from datetime import datetime
from enum import Enum as PyEnum
from app import db
from sqlalchemy import Text, JSON
import uuid
import pytz

# Enum classes for status tracking
class SubmissionStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    WARNING = "warning"

class TimelinesssClassification(PyEnum):
    ON_TIME = "on_time"
    LATE = "late"
    LAST_MINUTE_RUSH = "last_minute_rush"
    NO_DEADLINE = "no_deadline"

class UserRole(PyEnum):
    PROFESSOR = "professor"
    ADMIN = "admin"
    STUDENT = "student"

# Base model with common fields
class BaseModel(db.Model):
    __abstract__ = True
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# User model for professor authentication
class User(BaseModel):
    __tablename__ = 'users'
    
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # For basic auth (nullable for OAuth users)
    role = db.Column(db.Enum(UserRole), default=UserRole.PROFESSOR, nullable=False)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    submissions = db.relationship('Submission', backref='professor', lazy=True)
    deadlines = db.relationship('Deadline', backref='professor', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role.value,
            'profile_picture': self.profile_picture,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }

# Submission model - Core entity for document submissions
class Submission(BaseModel):
    __tablename__ = 'submissions'
    
    # Submission metadata
    job_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)  # SHA-256
    mime_type = db.Column(db.String(100), nullable=False)
    
    # Submission details
    submission_type = db.Column(db.String(50), nullable=False)  # 'upload' or 'drive_link'
    google_drive_link = db.Column(db.String(500), nullable=True)
    student_id = db.Column(db.String(50), nullable=True)
    student_name = db.Column(db.String(255), nullable=True)
    
    # Processing status
    status = db.Column(db.Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False)
    processing_started_at = db.Column(db.DateTime, nullable=True)
    processing_completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(Text, nullable=True)
    
    # Foreign keys
    professor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    deadline_id = db.Column(db.String(36), db.ForeignKey('deadlines.id'), nullable=True)
    
    # Relationships
    analysis_result = db.relationship('AnalysisResult', backref='submission', uselist=False, lazy=True)
    audit_logs = db.relationship('AuditLog', backref='submission', lazy=True)
    
    @property
    def is_late(self):
        """Check if submission was made after the deadline"""
        try:
            if not self.deadline_id:
                return False
            # Use a query to avoid lazy loading issues
            from app.models import Deadline
            deadline = Deadline.query.filter_by(id=self.deadline_id).first()
            if not deadline:
                return False
                
            # Handle timezone conversion
            # created_at is UTC (naive). Make it aware.
            created_at_utc = self.created_at.replace(tzinfo=pytz.UTC)
            
            # deadline_datetime is typically naive (representing local time in deadline.timezone)
            if deadline.timezone and deadline.timezone != 'UTC':
                try:
                    local_tz = pytz.timezone(deadline.timezone)
                    # Localize the naive deadline time to the specific timezone
                    deadline_aware = local_tz.localize(deadline.deadline_datetime)
                    # Convert to UTC for comparison
                    deadline_utc = deadline_aware.astimezone(pytz.UTC)
                    return created_at_utc > deadline_utc
                except Exception:
                    # Fallback if timezone invalid
                    pass
            
            # If standard UTC or fallback
            return self.created_at > deadline.deadline_datetime
        except Exception as e:
            return False
    
    @property
    def last_modified(self):
        """Return the last modification time (updated_at or created_at)"""
        return self.updated_at if self.updated_at else self.created_at
    
    @property
    def analysis_summary(self):
        """Return a summary of the analysis results"""
        if not self.analysis_result:
            return None
        return {
            'word_count': self.analysis_result.content_statistics.get('word_count') if self.analysis_result.content_statistics else None,
            'readability_score': self.analysis_result.flesch_kincaid_score,
            'is_complete': self.analysis_result.is_complete_document
        }
    
    def __repr__(self):
        return f'<Submission {self.job_id}>'
    
    def to_dict(self):
        # Ensure UTC timestamps are formatted with Z
        created_at_iso = self.created_at.isoformat()
        if not created_at_iso.endswith('Z') and not '+' in created_at_iso:
            created_at_iso += 'Z'
            
        last_modified_iso = self.last_modified.isoformat() if self.last_modified else None
        if last_modified_iso and not last_modified_iso.endswith('Z') and not '+' in last_modified_iso:
            last_modified_iso += 'Z'

        started_at_iso = self.processing_started_at.isoformat() if self.processing_started_at else None
        if started_at_iso and not started_at_iso.endswith('Z') and not '+' in started_at_iso:
            started_at_iso += 'Z'

        completed_at_iso = self.processing_completed_at.isoformat() if self.processing_completed_at else None
        if completed_at_iso and not completed_at_iso.endswith('Z') and not '+' in completed_at_iso:
            completed_at_iso += 'Z'

        return {
            'id': self.id,
            'job_id': self.job_id,
            'file_name': self.file_name,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'submission_type': self.submission_type,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'status': self.status.value,
            'is_late': self.is_late,
            'last_modified': last_modified_iso,
            'analysis_summary': self.analysis_summary,
            'created_at': created_at_iso,
            'processing_started_at': started_at_iso,
            'processing_completed_at': completed_at_iso,
            'error_message': self.error_message
        }

# Analysis Result model - Stores all analysis outputs
class AnalysisResult(BaseModel):
    __tablename__ = 'analysis_results'
    
    submission_id = db.Column(db.String(36), db.ForeignKey('submissions.id'), nullable=False, unique=True)
    
    # Module 2: Metadata and Content Analysis
    document_metadata = db.Column(JSON, nullable=True)  # Author, timestamps, etc.
    content_statistics = db.Column(JSON, nullable=True)  # Word count, sentences, pages
    document_text = db.Column(db.Text(length=4294967295), nullable=True)  # Full extracted text (LONGTEXT)
    
    # Module 3: Rule-based Insights
    heuristic_insights = db.Column(JSON, nullable=True)  # Timeliness, contribution analysis
    timeliness_classification = db.Column(db.Enum(TimelinesssClassification), nullable=True)
    contribution_growth_percentage = db.Column(db.Float, nullable=True)
    
    # Module 4: NLP Analysis
    nlp_results = db.Column(JSON, nullable=True)  # Readability, NER, term frequency
    flesch_kincaid_score = db.Column(db.Float, nullable=True)
    readability_grade = db.Column(db.String(50), nullable=True)
    named_entities = db.Column(JSON, nullable=True)
    top_terms = db.Column(JSON, nullable=True)
    
    # AI-generated insights (optional)
    ai_summary = db.Column(Text, nullable=True)
    ai_insights = db.Column(JSON, nullable=True)
    
    # Validation flags
    is_complete_document = db.Column(db.Boolean, default=True)
    validation_warnings = db.Column(JSON, nullable=True)
    
    # Processing metadata
    analysis_version = db.Column(db.String(50), default="1.0")
    processing_duration_seconds = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<AnalysisResult for {self.submission_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'document_metadata': self.document_metadata,
            'content_statistics': self.content_statistics,
            'heuristic_insights': self.heuristic_insights,
            'timeliness_classification': self.timeliness_classification.value if self.timeliness_classification else None,
            'contribution_growth_percentage': self.contribution_growth_percentage,
            'nlp_results': self.nlp_results,
            'flesch_kincaid_score': self.flesch_kincaid_score,
            'readability_grade': self.readability_grade,
            'named_entities': self.named_entities,
            'top_terms': self.top_terms,
            'ai_summary': self.ai_summary,
            'ai_insights': self.ai_insights,
            'is_complete_document': self.is_complete_document,
            'validation_warnings': self.validation_warnings,
            'analysis_version': self.analysis_version,
            'created_at': self.created_at.isoformat()
        }

# Deadline model for timeliness analysis
class Deadline(BaseModel):
    __tablename__ = 'deadlines'
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(Text, nullable=True)
    deadline_datetime = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Assignment details
    course_code = db.Column(db.String(50), nullable=True)
    assignment_type = db.Column(db.String(100), nullable=True)
    
    # Foreign key
    professor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    submissions = db.relationship('Submission', backref='deadline', lazy=True)
    
    def __repr__(self):
        return f'<Deadline {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline_datetime': self.deadline_datetime.isoformat(),
            'timezone': self.timezone,
            'course_code': self.course_code,
            'assignment_type': self.assignment_type,
            'professor_id': self.professor_id,
            'created_at': self.created_at.isoformat()
        }

# Document Snapshot model for version comparison
class DocumentSnapshot(BaseModel):
    __tablename__ = 'document_snapshots'
    
    file_id = db.Column(db.String(255), nullable=False, index=True)  # For tracking same document
    submission_id = db.Column(db.String(36), db.ForeignKey('submissions.id'), nullable=False)
    
    # Snapshot data
    word_count = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    snapshot_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadata for comparison
    major_changes = db.Column(db.Boolean, default=False)
    change_percentage = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<DocumentSnapshot {self.file_id} at {self.snapshot_timestamp}>'

# Audit Log model for compliance and tracking
class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'
    
    # Event details
    event_type = db.Column(db.String(100), nullable=False)  # submission, analysis, export, etc.
    event_description = db.Column(Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Associated entities
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    submission_id = db.Column(db.String(36), db.ForeignKey('submissions.id'), nullable=True)
    
    # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved word)
    event_metadata = db.Column(JSON, nullable=True)
    
    def __repr__(self):
        return f'<AuditLog {self.event_type} at {self.created_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'event_description': self.event_description,
            'user_id': self.user_id,
            'submission_id': self.submission_id,
            'ip_address': self.ip_address,
            'metadata': self.event_metadata,
            'created_at': self.created_at.isoformat()
        }

# Report Export model for tracking exports
class ReportExport(BaseModel):
    __tablename__ = 'report_exports'
    
    export_type = db.Column(db.String(20), nullable=False)  # 'pdf' or 'csv'
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    
    # Export parameters
    filter_parameters = db.Column(JSON, nullable=True)
    submissions_included = db.Column(JSON, nullable=True)  # List of submission IDs
    
    # User who requested export
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Export metadata
    download_count = db.Column(db.Integer, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<ReportExport {self.export_type} by {self.user_id}>'

# Session model for user session management
class UserSession(BaseModel):
    __tablename__ = 'user_sessions'
    
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # OAuth metadata
    google_access_token = db.Column(Text, nullable=True)  # Encrypted
    google_refresh_token = db.Column(Text, nullable=True)  # Encrypted
    token_expires_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<UserSession {self.session_token[:8]}... for {self.user_id}>'

# Submission Token model for student access
class SubmissionToken(BaseModel):
    __tablename__ = 'submission_tokens'
    
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    professor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    max_usage = db.Column(db.Integer, nullable=True)  # Optional usage limit
    
    professor = db.relationship('User', backref='submission_tokens')
    
    # Linked deadline
    deadline_id = db.Column(db.String(36), nullable=True)
    
    def __repr__(self):
        return f'<SubmissionToken {self.token[:8]}... by {self.professor_id}>'
    
    def is_valid(self):
        """Check if token is still valid"""
        if not self.is_active:
            return False
        if self.expires_at < datetime.utcnow():
            return False
        if self.max_usage and self.usage_count >= self.max_usage:
            return False
        return True