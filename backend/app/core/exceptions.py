"""
Custom exceptions for MetaDoc application

Provides a hierarchy of custom exceptions for better error handling
and more descriptive error messages throughout the application.
"""

class MetaDocException(Exception):
    """Base exception for all MetaDoc errors"""
    status_code = 500
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


class ValidationError(MetaDocException):
    """Raised when input validation fails"""
    status_code = 400
    
    def __init__(self, message, field=None):
        super().__init__(message, status_code=400)
        self.field = field


class AuthenticationError(MetaDocException):
    """Raised when authentication fails"""
    status_code = 401
    
    def __init__(self, message="Authentication required"):
        super().__init__(message, status_code=401)


class AuthorizationError(MetaDocException):
    """Raised when user lacks permission"""
    status_code = 403
    
    def __init__(self, message="Access denied"):
        super().__init__(message, status_code=403)


class ResourceNotFoundError(MetaDocException):
    """Raised when a requested resource is not found"""
    status_code = 404
    
    def __init__(self, resource_type, resource_id=None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, status_code=404)


class DuplicateResourceError(MetaDocException):
    """Raised when attempting to create a duplicate resource"""
    status_code = 409
    
    def __init__(self, resource_type, field=None):
        message = f"{resource_type} already exists"
        if field:
            message += f" with {field}"
        super().__init__(message, status_code=409)


class FileProcessingError(MetaDocException):
    """Raised when file processing fails"""
    status_code = 422
    
    def __init__(self, message="File processing failed"):
        super().__init__(message, status_code=422)


class DatabaseError(MetaDocException):
    """Raised when database operations fail"""
    status_code = 500
    
    def __init__(self, message="Database operation failed"):
        super().__init__(message, status_code=500)


class ExternalServiceError(MetaDocException):
    """Raised when external service (Google Drive, Gemini) fails"""
    status_code = 503
    
    def __init__(self, service_name, message=None):
        msg = f"{service_name} service unavailable"
        if message:
            msg += f": {message}"
        super().__init__(msg, status_code=503)
