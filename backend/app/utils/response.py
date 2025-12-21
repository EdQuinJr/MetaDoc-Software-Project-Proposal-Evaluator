"""
Standard response helpers for consistent API responses
"""

from flask import jsonify
from typing import Any, Dict, Optional

def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> tuple:
    """
    Create a standardized success response
    
    Args:
        data: Response data (dict, list, or any JSON-serializable object)
        message: Success message
        status_code: HTTP status code
    
    Returns:
        Tuple of (response, status_code)
    
    Example:
        return success_response(
            data={'user': user.to_dict()},
            message='User created successfully',
            status_code=201
        )
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response['data'] = data
    
    return jsonify(response), status_code


def error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[Dict] = None
) -> tuple:
    """
    Create a standardized error response
    
    Args:
        message: Error message
        status_code: HTTP status code
        errors: Optional dict of field-specific errors
    
    Returns:
        Tuple of (response, status_code)
    
    Example:
        return error_response(
            message='Validation failed',
            status_code=400,
            errors={'email': 'Invalid email format'}
        )
    """
    response = {
        'success': False,
        'error': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code


def paginated_response(
    items: list,
    page: int,
    per_page: int,
    total: int,
    message: str = "Success"
) -> tuple:
    """
    Create a standardized paginated response
    
    Args:
        items: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        message: Success message
    
    Returns:
        Tuple of (response, status_code)
    
    Example:
        return paginated_response(
            items=[user.to_dict() for user in users],
            page=1,
            per_page=20,
            total=100
        )
    """
    total_pages = (total + per_page - 1) // per_page
    
    response = {
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return jsonify(response), 200
