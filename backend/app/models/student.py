"""
Student model for Class Record tracking
"""

from app.core.extensions import db
from app.models.base import BaseModel

class Student(BaseModel):
    """Student model to track expected and registered students"""
    __tablename__ = 'students'
    
    student_id = db.Column(db.String(50), nullable=False) # ID number from Class Record
    last_name = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True) # Linked after registration
    
    # Registration status
    is_registered = db.Column(db.Boolean, default=False, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=True)
    
    # Foreign key to Deadline/Folder
    deadline_id = db.Column(db.String(36), db.ForeignKey('deadlines.id', ondelete='CASCADE'), nullable=False)
    
    # Unique constraint per folder/deadline to prevent duplicate student IDs in the same class
    __table_args__ = (
        db.UniqueConstraint('student_id', 'deadline_id', name='_student_deadline_uc'),
    )
    
    def __repr__(self):
        return f'<Student {self.student_id}: {self.last_name}, {self.first_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'email': self.email,
            'is_registered': self.is_registered,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'deadline_id': self.deadline_id,
            'status': 'Registered' if self.is_registered else 'Pending'
        }
