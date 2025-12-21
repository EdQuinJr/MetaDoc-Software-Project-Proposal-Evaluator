"""
Custom decorators for MetaDoc application
"""

from functools import wraps
from flask import request, jsonify
from app.core.exceptions import AuthenticationError

def require_authentication():
    """
    Decorator to require authentication for API endpoints
    
    Usage:
        @app.route('/protected')
        @require_authentication()
        def protected_route():
            user = request.current_user
            return {'message': 'Success'}
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # Get session token from Authorization header
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    raise AuthenticationError('Authentication required')
                
                session_token = auth_header[7:]
                
                # Validate session
                from app.api.auth import get_auth_service
                result, error = get_auth_service().validate_session(session_token)
                
                if error:
                    raise AuthenticationError(error)
                
                # Add user to request context
                request.current_user = result['user']
                request.current_session = result['session']
                
                return f(*args, **kwargs)
                
            except AuthenticationError as e:
                return jsonify({'error': str(e)}), 401
            except Exception as e:
                return jsonify({'error': 'Authentication error'}), 500
        
        return wrapper
    return decorator


def validate_json(*required_fields):
    """
    Decorator to validate JSON request body
    
    Usage:
        @app.route('/create', methods=['POST'])
        @validate_json('name', 'email')
        def create_user():
            data = request.get_json()
            return {'message': 'Success'}
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is required'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator


def rate_limit(max_requests=100, window_seconds=3600):
    """
    Simple rate limiting decorator
    
    Usage:
        @app.route('/api/endpoint')
        @rate_limit(max_requests=10, window_seconds=60)
        def limited_endpoint():
            return {'message': 'Success'}
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # TODO: Implement rate limiting logic
            # For now, just pass through
            return f(*args, **kwargs)
        
        return wrapper
    return decorator
