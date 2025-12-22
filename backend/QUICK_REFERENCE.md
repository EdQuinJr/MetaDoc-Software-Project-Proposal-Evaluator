# MetaDoc Backend - Quick Reference Guide

## 📁 New Directory Structure

```
app/
├── core/                    # Core infrastructure
│   ├── extensions.py        # Flask extensions (db, migrate, jwt, cors)
│   ├── exceptions.py        # Custom exceptions
│   └── constants.py         # App-wide constants
│
├── models/                  # Database models (split by domain)
│   ├── base.py             # BaseModel, enums
│   ├── user.py             # User, UserSession
│   ├── submission.py       # Submission, SubmissionToken
│   ├── deadline.py         # Deadline
│   ├── analysis.py         # AnalysisResult, DocumentSnapshot
│   ├── audit.py            # AuditLog
│   └── report.py           # ReportExport
│
├── api/                     # API route handlers
│   ├── auth.py             # /api/v1/auth/*
│   ├── submission.py       # /api/v1/submission/*
│   ├── dashboard.py        # /api/v1/dashboard/*
│   ├── metadata.py         # /api/v1/metadata/*
│   ├── insights.py         # /api/v1/insights/*
│   ├── nlp.py              # /api/v1/nlp/*
│   └── reports.py          # /api/v1/reports/*
│
├── services/                # Business logic
│   ├── audit_service.py
│   └── validation_service.py
│
└── utils/                   # Utility functions
    ├── decorators.py        # @require_authentication, @validate_json
    ├── response.py          # success_response(), error_response()
    └── file_utils.py        # FileUtils class
```

## 🔧 Common Import Patterns

### Models
```python
# Import specific models
from app.models import User, Submission, Deadline

# Import enums
from app.models import SubmissionStatus, UserRole

# Import base
from app.models.base import BaseModel
```

### Core
```python
# Extensions
from app.core.extensions import db, migrate, jwt

# Exceptions
from app.core.exceptions import (
    ValidationError,
    AuthenticationError,
    ResourceNotFoundError
)

# Constants
from app.core.constants import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    SubmissionStatus
)
```

### Utilities
```python
# Decorators
from app.utils import require_authentication, validate_json

# Responses
from app.utils import success_response, error_response

# File utilities
from app.utils import FileUtils
```

## 💡 Usage Examples

### Creating a Protected Route
```python
from flask import Blueprint, request
from app.utils import require_authentication, success_response

bp = Blueprint('example', __name__)

@bp.route('/protected')
@require_authentication()
def protected_route():
    user = request.current_user
    return success_response(
        data={'user': user.to_dict()},
        message='Access granted'
    )
```

### Using Custom Exceptions
```python
from app.core.exceptions import ValidationError, ResourceNotFoundError

def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ResourceNotFoundError('User', user_id)
    return user

def validate_email(email):
    if not email or '@' not in email:
        raise ValidationError('Invalid email format', field='email')
```

### Standard Responses
```python
from app.utils import success_response, error_response

# Success
return success_response(
    data={'items': [item.to_dict() for item in items]},
    message='Items retrieved successfully'
)

# Error
return error_response(
    message='Validation failed',
    status_code=400,
    errors={'email': 'Required field'}
)
```

### Working with Models
```python
from app.models import Submission, SubmissionStatus
from app.core.extensions import db

# Create
submission = Submission(
    job_id='12345',
    file_name='document.docx',
    status=SubmissionStatus.PENDING
)
db.session.add(submission)
db.session.commit()

# Query
submissions = Submission.query.filter_by(
    status=SubmissionStatus.COMPLETED
).all()

# Update
submission.status = SubmissionStatus.PROCESSING
db.session.commit()
```

## 🎯 Key Benefits

### Before Refactoring
- ❌ 17KB monolithic models.py
- ❌ Mixed concerns in route files
- ❌ Scattered constants
- ❌ Inconsistent error handling

### After Refactoring
- ✅ ~2KB focused model files
- ✅ Clear separation of concerns
- ✅ Centralized constants
- ✅ Consistent error handling
- ✅ Reusable utilities
- ✅ Better IDE support

## 📝 File Locations

### Configuration
- `config.py` - Environment configurations
- `app/__init__.py` - App factory
- `app/core/constants.py` - Constants

### Models
- `app/models/*.py` - All database models
- Old backup: `app/models_old.py.bak`

### API Routes
- `app/api/*.py` - All route handlers

### Business Logic
- `app/services/*.py` - Service classes

### Utilities
- `app/utils/*.py` - Helper functions
- `scripts/*.py` - Utility scripts

## 🚀 Quick Commands

```bash
# Start backend
python run.py

# Reset database
python scripts/reset_database.py

# Install dependencies
pip install -r requirements.txt

# Run with specific config
FLASK_ENV=production python run.py
```

## 🔍 Finding Things

**Need to add a new model?**
→ Create `app/models/your_model.py` and export in `app/models/__init__.py`

**Need to add a new API route?**
→ Add to existing file in `app/api/` or create new blueprint

**Need a new utility function?**
→ Add to `app/utils/` and export in `__init__.py`

**Need to change a constant?**
→ Update `app/core/constants.py`

**Need a new exception type?**
→ Add to `app/core/exceptions.py`

## ⚠️ Important Notes

1. **Always import models from `app.models`**, not from individual files
2. **Use custom exceptions** instead of generic ones
3. **Use response helpers** for consistent API responses
4. **Use decorators** for common functionality
5. **Keep API routes thin** - business logic goes in services

## 📚 Documentation Files

- `BACKEND_SUMMARY.md` - Complete architecture overview
- `QUICK_REFERENCE.md` - This file (quick reference)
- `README.md` - Comprehensive documentation
- `app/schemas/dto/README.md` - DTO usage guide
- `GOOGLE_DRIVE_SETUP.md` - Google Drive setup

## 🏗️ Architecture Overview

```
API Layer (Controllers)
    ↓ uses
Service Layer (Business Logic)
    ↓ uses
Persistence Layer (Database)
```

**10 Service Classes:**
- AuthService, SubmissionService, DriveService
- MetadataService, NLPService, InsightsService
- DashboardService, ReportService
- AuditService, ValidationService

---

**Last Updated:** December 22, 2025
**Backend Status:** ✅ Running on http://localhost:5000
**Architecture:** 3-Layer with Complete Service Separation
