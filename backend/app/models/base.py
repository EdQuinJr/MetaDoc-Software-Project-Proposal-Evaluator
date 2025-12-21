"""
Base model and enums for MetaDoc database models
"""

from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.core.extensions import db
from sqlalchemy import Text, JSON

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
