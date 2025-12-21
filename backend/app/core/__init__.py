"""
Core module for MetaDoc backend

This module contains core functionality including:
- Database and extension initialization
- Custom exceptions
- Application constants
"""

from app.core.extensions import db, migrate, jwt, cors
from app.core.exceptions import (
    MetaDocException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    DuplicateResourceError
)

__all__ = [
    'db',
    'migrate', 
    'jwt',
    'cors',
    'MetaDocException',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'ResourceNotFoundError',
    'DuplicateResourceError'
]
