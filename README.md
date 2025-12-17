# MetaDoc: Software Project Proposal Evaluator

MetaDoc is a Google Drive-integrated metadata analyzer for academic document evaluation, designed to enhance the fairness, transparency, and efficiency of academic document assessment within IT and Computer Science programs.

## 🏗️ System Overview

The system consists of:
- **Backend API**: Flask-based REST API with Google OAuth2 integration
- **Frontend**: React application with responsive design
- **Database**: MySQL/SQLite for data storage
- **Google Integration**: Drive API and OAuth2 authentication

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+**
- **MySQL Server** (optional - SQLite works for development)
- **Google Cloud Account** (for OAuth and Drive API)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd MetaDoc-Software-Project-Proposal-Evaluator
```

2. **Setup Backend** (5 minutes):
```bash
cd backend
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Install dependencies (minimal - without NLP)
pip install -r requirements-minimal.txt

# Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env with your Google OAuth credentials

# Initialize database
python database_setup.py init

# Start server
python run.py
```

Backend will be available at: `http://localhost:5000`

3. **Setup Frontend**:
```bash
cd frontend/metadoc
npm install

# Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env with your settings

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000` or `http://localhost:5173`

## 📖 Detailed Setup Guide

For detailed setup instructions, troubleshooting, and configuration options, see:

- **[📘 Complete Setup Instructions](SETUP_INSTRUCTIONS.md)** - Comprehensive guide for team members
- **[🔧 Backend Documentation](backend/README.md)** - Backend API details
- **[🎨 Frontend Documentation](frontend/metadoc/README.md)** - Frontend development guide

## 🔑 Google Cloud Setup (Required)

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one

### 2. Enable Required APIs

- Navigate to "APIs & Services" → "Library"
- Enable these APIs:
  - **Google Drive API**
  - **Google OAuth2 API**

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Choose "Web application"
4. Add these Authorized redirect URIs:
   ```
   http://localhost:5000/auth/google/callback
   http://127.0.0.1:5000/auth/google/callback
   ```
5. Save your **Client ID** and **Client Secret**

### 4. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "Internal" (for organization) or "External"
3. Fill required fields:
   - App name: "MetaDoc"
   - User support email: Your email
   - Developer contact: Your email

## ⚙️ Configuration

### Backend (.env)

```env
# Database (SQLite for development)
DATABASE_URL=sqlite:///metadoc.db

# Google OAuth2 (Required)
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# Security
SECRET_KEY=your_super_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Institution Settings
ALLOWED_EMAIL_DOMAINS=cit.edu,yourdomain.edu
INSTITUTION_NAME=Your Institution Name
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
VITE_GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
```

## 🎯 Features

### Module 1: File Submission & Retrieval
- Upload DOCX files or provide Google Drive links
- Automatic file validation and virus scanning
- Support for multiple file formats

### Module 2: Metadata Extraction
- Automatic extraction of document properties
- Content analysis and statistics
- Version tracking and history

### Module 3: Rule-Based Insights
- Deadline monitoring and timeliness analysis
- Contribution tracking
- Automated compliance checking

### Module 4: NLP Analysis (Optional)
- Readability scoring
- Content trends analysis
- Named entity recognition
- AI-assisted insights

### Module 5: Dashboard & Reports
- Comprehensive professor dashboard
- Submission management
- PDF and CSV report generation
- Analytics and visualizations

## 🔧 Development

### Project Structure

```
MetaDoc-Software-Project-Proposal-Evaluator/
├── backend/
│   ├── app/
│   │   ├── modules/          # Feature modules
│   │   ├── models.py          # Database models
│   │   └── __init__.py        # App factory
│   ├── requirements.txt       # Full dependencies
│   ├── requirements-minimal.txt  # Core dependencies
│   ├── run.py                 # Application entry point
│   └── config.py              # Configuration
├── frontend/
│   └── metadoc/
│       ├── src/
│       └── package.json
└── SETUP_INSTRUCTIONS.md      # Detailed setup guide
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend/metadoc
npm test
```

## 🐛 Common Issues

### Backend Won't Start

**Issue**: `ModuleNotFoundError: No module named 'flask_jwt_extended'`

**Solution**: 
```bash
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Reinstall dependencies
pip install -r requirements-minimal.txt
```

### Google OAuth Error

**Issue**: `Error 400: redirect_uri_mismatch`

**Solution**: Ensure redirect URI in `.env` exactly matches Google Cloud Console (no trailing slashes)

### Database Error

**Issue**: Database connection failed

**Solution**: For development, use SQLite (no setup needed):
```env
DATABASE_URL=sqlite:///metadoc.db
```

For more troubleshooting, see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

## 📱 Usage

1. **Access the application**: `http://localhost:3000`
2. **Login with Google**: Use institutional email
3. **Submit documents**: Upload files or provide Google Drive links
4. **View analysis**: Check dashboard for insights and reports
5. **Export reports**: Generate PDF or CSV reports

## 🏫 Institution Configuration

Update the `.env` file with your institution settings:

```env
ALLOWED_EMAIL_DOMAINS=yourdomain.edu,anotherdomain.edu.ph
INSTITUTION_NAME=Your Institution Name
```

Only users with emails from allowed domains can access the system.

## 📚 Documentation

- **[Complete Setup Guide](SETUP_INSTRUCTIONS.md)** - Detailed installation and configuration
- **[Backend API Documentation](backend/README.md)** - API endpoints and usage
- **[Frontend Documentation](frontend/metadoc/README.md)** - Frontend development
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions

## 🤝 Contributing

### For Team Members

1. **Before starting work**:
   - Pull latest changes: `git pull`
   - Activate virtual environment
   - Install any new dependencies

2. **Before committing**:
   - Test your changes locally
   - Update documentation if needed
   - Don't commit `.env` files
   - Update `requirements.txt` if you added packages

3. **Code style**:
   - Follow PEP 8 for Python
   - Use ESLint for JavaScript/React
   - Add comments for complex logic
   - Write descriptive commit messages

## 📄 License

This project is developed for Cebu Institute of Technology – University as part of the capstone project requirements.

## 👥 Development Team

- **Edgar B. Quiandao Jr.** - Backend Developer
- **Paul G. Abellana** - Backend Developer
- **Miguel Ray A. Veloso** - Frontend Developer
- **Mark Christian Q. Garing** - Full Stack Developer

**Advisers**: Mr. Ralph Laviste & Dr. Cheryl Pantaleon

---

## 🆘 Need Help?

- **Setup Issues**: See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
- **API Questions**: See [backend/README.md](backend/README.md)
- **Bug Reports**: Contact the development team
- **Feature Requests**: Discuss with advisers

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Institution**: Cebu Institute of Technology - University
