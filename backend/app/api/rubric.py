"""
Rubric API Endpoints
"""

from flask import Blueprint, request, jsonify, g
from app.core.extensions import db
from app.models import Rubric, UserRole, UserSession
from app.utils.decorators import require_authentication
from datetime import datetime

rubric_bp = Blueprint('rubric', __name__, url_prefix='/api/rubrics')

@rubric_bp.route('/', methods=['GET'])
@require_authentication()
def get_rubrics():
    """Get all rubrics for the authenticated professor"""
    try:
        user = request.current_user
        
        # Only professors can manage rubrics
        if user.role != UserRole.PROFESSOR:
            return jsonify({'error': 'Unauthorized'}), 403
            
        rubrics = Rubric.query.filter_by(professor_id=user.id).order_by(Rubric.created_at.desc()).all()
        
        return jsonify({
            'rubrics': [rubric.to_dict() for rubric in rubrics]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rubric_bp.route('/', methods=['POST'])
@require_authentication()
def create_rubric():
    """Create a new rubric"""
    try:
        user = request.current_user
        if user.role != UserRole.PROFESSOR:
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.json
        if not data or not data.get('title') or not data.get('criteria'):
            return jsonify({'error': 'Title and criteria are required'}), 400
            
        # Basic validation of criteria
        criteria = data.get('criteria')
        if not isinstance(criteria, list) or len(criteria) == 0:
            return jsonify({'error': 'Criteria must be a non-empty list'}), 400
            
        rubric = Rubric(
            title=data.get('title'),
            description=data.get('description'),
            criteria=criteria,
            professor_id=user.id
        )
        
        db.session.add(rubric)
        db.session.commit()
        
        return jsonify({
            'message': 'Rubric created successfully',
            'rubric': rubric.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rubric_bp.route('/<rubric_id>', methods=['GET'])
@require_authentication()
def get_rubric(rubric_id):
    """Get a specific rubric"""
    try:
        user = request.current_user
        rubric = Rubric.query.filter_by(id=rubric_id, professor_id=user.id).first()
        
        if not rubric:
            return jsonify({'error': 'Rubric not found'}), 404
            
        return jsonify({'rubric': rubric.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rubric_bp.route('/<rubric_id>', methods=['PUT'])
@require_authentication()
def update_rubric(rubric_id):
    """Update a specific rubric"""
    try:
        user = request.current_user
        rubric = Rubric.query.filter_by(id=rubric_id, professor_id=user.id).first()
        
        if not rubric:
            return jsonify({'error': 'Rubric not found'}), 404
            
        data = request.json
        if 'title' in data:
            rubric.title = data['title']
        if 'description' in data:
            rubric.description = data['description']
        if 'criteria' in data:
            if not isinstance(data['criteria'], list) or len(data['criteria']) == 0:
                 return jsonify({'error': 'Criteria must be a non-empty list'}), 400
            rubric.criteria = data['criteria']
            
        db.session.commit()
        
        return jsonify({
            'message': 'Rubric updated successfully',
            'rubric': rubric.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rubric_bp.route('/<rubric_id>', methods=['DELETE'])
@require_authentication()
def delete_rubric(rubric_id):
    """Delete a specific rubric"""
    try:
        user = request.current_user
        rubric = Rubric.query.filter_by(id=rubric_id, professor_id=user.id).first()
        
        if not rubric:
            return jsonify({'error': 'Rubric not found'}), 404
            
        db.session.delete(rubric)
        db.session.commit()
        
        return jsonify({'message': 'Rubric deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
