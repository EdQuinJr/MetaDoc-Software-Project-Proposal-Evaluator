"""
Rubric model
"""

from sqlalchemy import Text, JSON
from app.core.extensions import db
from app.models.base import BaseModel

class Rubric(BaseModel):
    """Rubric model for qualitative evaluation guidance"""
    __tablename__ = 'rubrics'
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(Text, nullable=True)
    
    # Stores list of criteria: 
    # [{ "name": "Clarity", "description": "...", "weight": "High" }]
    criteria = db.Column(JSON, nullable=False, default=list)
    
    # Foreign key (created by professor)
    professor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Relationship with deadlines
    deadlines = db.relationship('Deadline', backref='rubric', lazy=True)
    
    def __repr__(self):
        return f'<Rubric {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'criteria': self.criteria,
            'professor_id': self.professor_id,
            'created_at': self.created_at.isoformat()
        }
