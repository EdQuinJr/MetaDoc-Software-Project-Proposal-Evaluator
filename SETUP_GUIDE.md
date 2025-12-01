# MetaDoc Setup Guide

Complete setup instructions for the MetaDoc application (Frontend + Backend).

## Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** and npm (for frontend)
- **MySQL or PostgreSQL** (for database)
- **Google Cloud Project** with OAuth 2.0 credentials
- **Google Service Account** for Drive API access

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Database
DATABASE_URL=mysql://username:password@localhost/metadoc
# Or for SQLite (development):
# DATABASE_URL=sqlite:///metadoc.db

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/v1/auth/callback
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json

# Gemini AI (Optional)
GEMINI_API_KEY=your-gemini-api-key

# Institution Settings
ALLOWED_EMAIL_DOMAINS=cit.edu,example.edu
INSTITUTION_NAME=Cebu Institute of Technology - University

# File Storage
UPLOAD_FOLDER=./uploads
TEMP_STORAGE_PATH=./temp_files
REPORTS_STORAGE_PATH=./reports
MAX_CONTENT_LENGTH=52428800

# Session & Security
SESSION_TIMEOUT=3600
ENABLE_AUDIT_LOGGING=True
```

### 6. Initialize Database

```bash
python database_setup.py
```

Or using Flask-Migrate:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Run Backend Server

```bash
python run.py
```

The backend will be available at `http://localhost:5000`

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend/metadoc
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the `frontend/metadoc` directory:

```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

### 4. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 5. Build for Production

```bash
npm run build
```

---

## Google Cloud Configuration

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the following APIs:
   - Google Drive API
   - Google OAuth 2.0

### 2. Configure OAuth 2.0

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth 2.0 Client ID**
3. Configure consent screen
4. Set application type to **Web application**
5. Add authorized redirect URIs:
   - `http://localhost:5000/api/v1/auth/callback`
   - Your production callback URL
6. Save the Client ID and Client Secret

### 3. Create Service Account

1. Go to **IAM & Admin > Service Accounts**
2. Create a new service account
3. Grant it **Viewer** role
4. Create and download JSON key
5. Save the JSON file and reference it in `GOOGLE_SERVICE_ACCOUNT_FILE`

---

## Testing the Application

### 1. Start Backend

```bash
cd backend
python run.py
```

### 2. Start Frontend

```bash
cd frontend/metadoc
npm run dev
```

### 3. Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

### 4. Login

Click "Sign in with Google" and authenticate with an institutional email.

---

## Features Implemented

### ✅ Module 1: File Submission & Retrieval
- File upload (DOCX/DOC)
- Google Drive link submission
- File validation
- Permission guidance

### ✅ Module 2: Metadata Extraction
- Author, timestamps, file size
- Word count, character count, sentences
- Document completeness validation

### ✅ Module 3: Rule-Based Insights
- Timeliness classification (On-time, Late, Last-Minute Rush)
- Contribution growth analysis
- Deadline management

### ✅ Module 4: NLP Analysis
- Flesch-Kincaid readability score
- Named Entity Recognition (NER)
- Term frequency analysis
- Optional Gemini AI summaries

### ✅ Module 5: Professor Dashboard
- OAuth 2.0 authentication
- Submission overview
- Detailed report viewing
- Export to PDF/CSV

### ✅ Frontend Features
- Maroon & Gold theme (CIT-U branding)
- Responsive design (mobile, tablet, desktop)
- Clean, modern UI with cards and badges
- Real-time submission tracking
- Intuitive navigation

---

## Troubleshooting

### Backend Issues

**Database Connection Error:**
- Verify DATABASE_URL is correct
- Ensure database server is running
- Check user permissions

**Google OAuth Error:**
- Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- Check redirect URI matches Google Cloud Console
- Ensure email domain is in ALLOWED_EMAIL_DOMAINS

**File Upload Error:**
- Check UPLOAD_FOLDER and TEMP_STORAGE_PATH exist
- Verify file permissions
- Ensure MAX_CONTENT_LENGTH is appropriate

### Frontend Issues

**API Connection Error:**
- Verify backend is running on port 5000
- Check VITE_API_BASE_URL in .env
- Ensure CORS is configured correctly

**Build Error:**
- Delete node_modules and package-lock.json
- Run `npm install` again
- Check Node.js version (18+)

---

## Production Deployment

### Backend

1. Set `FLASK_ENV=production`
2. Use a production database (MySQL/PostgreSQL)
3. Configure proper SECRET_KEY and JWT_SECRET_KEY
4. Enable HTTPS
5. Set up reverse proxy (Nginx/Apache)
6. Use a process manager (Gunicorn, uWSGI)

### Frontend

1. Build the application: `npm run build`
2. Serve the `dist` folder with a web server
3. Update VITE_API_BASE_URL to production backend URL
4. Configure HTTPS
5. Set up CDN for static assets (optional)

---

## Support

For issues or questions:
- Check the SRS document for requirements
- Review backend API documentation in `run.py`
- Check frontend README in `frontend/metadoc/README.md`

---

## License

© 2025 MetaDoc - Cebu Institute of Technology University
All rights reserved.
