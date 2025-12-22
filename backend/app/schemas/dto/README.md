# Data Transfer Objects (DTOs)

## Overview
DTOs provide a clean separation between database models and API responses. They control what data is exposed, format responses consistently, and hide sensitive information.

## Benefits
- **Security**: Hide sensitive fields (passwords, internal IDs)
- **Consistency**: Standardized response format across all endpoints
- **Flexibility**: Different views of the same data (list vs detail)
- **Maintainability**: Centralized serialization logic

## Usage Examples

### Basic Serialization
```python
from app.schemas.dto import UserDTO, SubmissionDTO

# Serialize a single user
user_data = UserDTO.serialize(user)

# Serialize a list of users
users_data = UserDTO.serialize_list(users)
```

### In API Routes
```python
from flask import jsonify
from app.schemas.dto import SubmissionDetailDTO, SubmissionListDTO

# List view - minimal data
@app.route('/submissions')
def get_submissions():
    submissions = Submission.query.all()
    return jsonify({
        'submissions': SubmissionListDTO.serialize_list(submissions)
    })

# Detail view - full data
@app.route('/submissions/<id>')
def get_submission(id):
    submission = Submission.query.get(id)
    return jsonify({
        'submission': SubmissionDetailDTO.serialize(submission)
    })
```

### With Options
```python
from app.schemas.dto import AnalysisResultDTO, DeadlineDTO

# Include/exclude specific fields
analysis_data = AnalysisResultDTO.serialize(analysis, include_full_text=False)

# Include related data
deadline_data = DeadlineDTO.serialize(deadline, include_submissions=True)
```

## Available DTOs

### User DTOs
- `UserDTO` - Basic user information
- `UserProfileDTO` - User profile with statistics
- `UserSessionDTO` - Session information

### Submission DTOs
- `SubmissionDTO` - Basic submission data
- `SubmissionListDTO` - Minimal data for list views
- `SubmissionDetailDTO` - Full submission details with relations
- `SubmissionTokenDTO` - Submission token information

### Analysis DTOs
- `AnalysisResultDTO` - Complete analysis results
- `MetadataDTO` - Document metadata
- `ContentStatisticsDTO` - Content statistics
- `HeuristicInsightsDTO` - Heuristic analysis insights
- `NLPResultDTO` - NLP analysis results

### Other DTOs
- `DeadlineDTO` - Deadline information
- `DeadlineListDTO` - Minimal deadline data for lists
- `ReportExportDTO` - Report export information

## Migration from .to_dict()

### Before (using model.to_dict())
```python
return jsonify({
    'submission': submission.to_dict()
})
```

### After (using DTOs)
```python
from app.schemas.dto import SubmissionDTO

return jsonify({
    'submission': SubmissionDTO.serialize(submission)
})
```

## Best Practices

1. **Use specific DTOs for different views**
   - List views: Use `*ListDTO` for minimal data
   - Detail views: Use `*DetailDTO` for complete data

2. **Don't expose sensitive data**
   - Never include passwords, tokens, or internal keys
   - DTOs automatically filter sensitive fields

3. **Keep DTOs focused**
   - Each DTO should have a single responsibility
   - Create new DTOs for different use cases

4. **Use options for flexibility**
   - Add boolean parameters for optional data
   - Example: `include_analysis`, `include_full_text`

5. **Handle None values**
   - All DTOs handle None inputs gracefully
   - Returns None or empty dict as appropriate
