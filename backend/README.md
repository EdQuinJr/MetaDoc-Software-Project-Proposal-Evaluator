# MetaDoc Backend API

MetaDoc is a Google Drive-integrated metadata analyzer for academic document evaluation. This backend API implements the complete system architecture as specified in the Software Requirements Specifications (SRS).

## 🏗️ Architecture Overview

The system follows a modular architecture with 5 main modules:

1. **Module 1**: File Submission, Retrieval, and Validation
2. **Module 2**: Metadata Extraction & Content Analysis  
3. **Module 3**: Rule-Based AI Insights and Deadline Monitoring
4. **Module 4**: NLP-Based Readability, Content Trends, and AI-Assisted Insights
5. **Module 5**: Professor Dashboard and Report Management

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MySQL or PostgreSQL database
- Google Cloud Project with Drive API enabled
- (Optional) Google Gemini AI API key

### Installation

1. **Clone and setup environment:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
copy .env.example .env
# Edit .env with your configuration
```

3. **Setup database:**
```bash
python database_setup.py init
python database_setup.py sample  # Optional: Create sample data
```

4. **Download NLP models:**
```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

5. **Start the server:**
```bash
python run.py
```

The server will start on `http://localhost:5000`

## 🔧 Configuration

### Required Environment Variables

```env
# Database
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/metadoc_db

# Google OAuth (Required)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account-key.json

# Security
SECRET_KEY=your_super_secret_key
JWT_SECRET_KEY=your_jwt_secret_key

# Optional: AI Features
GEMINI_API_KEY=your_gemini_api_key

# Institution Settings
ALLOWED_EMAIL_DOMAINS=cit.edu,school.edu.ph
INSTITUTION_NAME=Cebu Institute of Technology - University
```

### Google Cloud Setup

1. **Create Google Cloud Project**
2. **Enable APIs:**
   - Google Drive API
   - Google OAuth2 API
3. **Create OAuth 2.0 Credentials:**
   - Add authorized redirect URI: `http://localhost:5000/api/v1/auth/callback`
4. **Create Service Account:**
   - Download JSON key file
   - Grant Drive access permissions

## 📡 API Endpoints

### Authentication
- `GET /api/v1/auth/login` - Initiate OAuth login
- `GET /api/v1/auth/callback` - Handle OAuth callback
- `POST /api/v1/auth/validate` - Validate session token
- `POST /api/v1/auth/logout` - Logout user

### File Submission (Module 1)
- `POST /api/v1/submission/upload` - Upload DOCX file
- `POST /api/v1/submission/drive-link` - Submit Google Drive link
- `GET /api/v1/submission/status/<job_id>` - Check submission status
- `POST /api/v1/submission/validate-link` - Validate Drive link

### Metadata Analysis (Module 2)
- `POST /api/v1/metadata/analyze/<submission_id>` - Start analysis
- `GET /api/v1/metadata/result/<submission_id>` - Get analysis results
- `POST /api/v1/metadata/reprocess/<submission_id>` - Reprocess submission

### Heuristic Insights (Module 3)
- `POST /api/v1/insights/analyze/<submission_id>` - Generate insights
- `GET /api/v1/insights/timeliness/<submission_id>` - Timeliness analysis
- `GET /api/v1/insights/contribution/<submission_id>` - Contribution analysis

### NLP Analysis (Module 4)
- `POST /api/v1/nlp/analyze/<submission_id>` - Full NLP analysis
- `GET /api/v1/nlp/readability/<submission_id>` - Readability analysis
- `GET /api/v1/nlp/entities/<submission_id>` - Named entity recognition

### Dashboard (Module 5)
- `GET /api/v1/dashboard/overview` - Dashboard statistics
- `GET /api/v1/dashboard/submissions` - Submissions list (with filters)
- `GET /api/v1/dashboard/submissions/<id>` - Submission details
- `GET /api/v1/dashboard/deadlines` - Deadlines list
- `POST /api/v1/dashboard/deadlines` - Create deadline
- `PUT /api/v1/dashboard/deadlines/<id>` - Update deadline

### Reports
- `POST /api/v1/reports/export/pdf` - Export PDF report
- `POST /api/v1/reports/export/csv` - Export CSV report
- `GET /api/v1/reports/download/<export_id>` - Download report
- `GET /api/v1/reports/exports` - Export history

## 🔐 Authentication & Security

### OAuth 2.0 Flow
1. Frontend redirects to `/api/v1/auth/login`
2. User authenticates with Google
3. Google redirects to callback with authorization code
4. Backend exchanges code for tokens and creates session
5. Session token returned for subsequent API calls

### Request Authentication
Include session token in Authorization header:
```
Authorization: Bearer <session_token>
```

### Security Features
- TLS encryption (enforced in production)
- Domain-based access control
- Session timeout management
- Audit logging for compliance
- Data anonymization for AI processing
- File validation and virus scanning

## 📊 Database Schema

### Core Tables
- `users` - Professor accounts
- `submissions` - Document submissions
- `analysis_results` - Analysis outputs
- `deadlines` - Assignment deadlines
- `document_snapshots` - Version tracking
- `audit_logs` - Compliance logging
- `user_sessions` - Session management
- `report_exports` - Export tracking

### Data Privacy Compliance
- Automatic data cleanup based on retention policies
- Audit trail for all data access
- Data anonymization for external AI services
- GDPR-like data export functionality

## 🧪 Testing & Development

### Database Management
```bash
# Initialize database
python database_setup.py init

# Create sample data
python database_setup.py sample

# Verify database setup
python database_setup.py verify
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask pytest-mock

# Run tests
pytest tests/
```

### API Testing
Use the provided Postman collection or test with curl:

```bash
# Test file upload
curl -X POST http://localhost:5000/api/v1/submission/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.docx" \
  -F "student_name=John Doe"

# Test Google Drive link
curl -X POST http://localhost:5000/api/v1/submission/drive-link \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"drive_link": "https://drive.google.com/file/d/FILE_ID"}'
```

## 📈 Performance & Scalability

### Performance Requirements (SRS Compliance)
- Document processing: ≤10 seconds for standard files
- File upload: ≤5 seconds for files under 10MB
- Concurrent processing: Up to 5 simultaneous analysis jobs
- API response time: <2 seconds for most endpoints

### Optimization Features
- Asynchronous file processing
- Database query optimization
- Efficient NLP processing with model caching
- Background cleanup tasks
- Rate limiting and request throttling

## 🔍 Monitoring & Logging

### Audit Logging
All significant events are logged for compliance:
- User authentication
- File submissions and processing
- Data access and exports
- System configuration changes

### Error Handling
- Structured error responses
- Comprehensive logging
- Graceful degradation for optional features
- User-friendly error messages

## 🚀 Deployment

### Production Considerations
1. **Environment Setup:**
   - Set `FLASK_ENV=production`
   - Use production database
   - Configure HTTPS/TLS
   - Set up proper logging

2. **Security Hardening:**
   - Secure credential storage
   - Network security
   - Regular security updates
   - Backup and recovery procedures

3. **Scaling Options:**
   - Horizontal scaling with load balancer
   - Database read replicas
   - File storage scaling
   - Background job processing

### Docker Deployment
```dockerfile
# Example Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "run.py"]
```

## 📝 API Usage Examples

### Complete Workflow Example

1. **Authenticate:**
```javascript
// Frontend redirects to login
window.location.href = '/api/v1/auth/login';
// After callback, get session token
const sessionToken = 'received_token';
```

2. **Submit Document:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('student_name', 'John Doe');

const response = await fetch('/api/v1/submission/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${sessionToken}`
  },
  body: formData
});

const result = await response.json();
const jobId = result.job_id;
```

3. **Process Document:**
```javascript
// Start metadata analysis
await fetch(`/api/v1/metadata/analyze/${submissionId}`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${sessionToken}`
  }
});

// Generate insights
await fetch(`/api/v1/insights/analyze/${submissionId}`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${sessionToken}`
  }
});

// Run NLP analysis
await fetch(`/api/v1/nlp/analyze/${submissionId}`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${sessionToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ enable_ai_summary: true })
});
```

4. **View Results:**
```javascript
const submission = await fetch(`/api/v1/dashboard/submissions/${submissionId}`, {
  headers: {
    'Authorization': `Bearer ${sessionToken}`
  }
}).then(r => r.json());
```

5. **Export Report:**
```javascript
const exportResponse = await fetch('/api/v1/reports/export/pdf', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${sessionToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    submission_ids: [submissionId]
  })
});

const exportResult = await exportResponse.json();
// Download using: /api/v1/reports/download/${exportResult.export_id}
```

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Add comprehensive docstrings
3. Include unit tests for new features
4. Update API documentation
5. Ensure SRS compliance

## 📄 License

This project is developed for Cebu Institute of Technology – University as part of the capstone project requirements.

## 👥 Development Team

- Edgar B. Quiandao Jr.
- Paul G. Abellana  
- Miguel Ray A. Veloso
- Mark Christian Q. Garing

**Advisers:** Mr. Ralph Laviste & Dr. Cheryl Pantaleon

---

For questions or support, please contact the development team or refer to the complete SRS documentation.