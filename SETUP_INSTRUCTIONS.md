# MetaDoc Backend Setup Instructions

**Last Updated**: December 18, 2025  
**Tested On**: Windows 11, Python 3.13

This guide provides step-by-step instructions for setting up the MetaDoc backend for development.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** (Download from [python.org](https://www.python.org/downloads/))
  - ✅ Tested and working on Python 3.13
  - ✅ Tested and working on Python 3.10-3.12
- **Git** (for cloning the repository)
- **MySQL Server** (optional - SQLite works fine for development)
- **Google Cloud Account** (for OAuth and Drive API)

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd MetaDoc-Software-Project-Proposal-Evaluator/backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv

# Linux/Mac
python3 -m venv venv
```

### 3. Activate Virtual Environment

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

> **⚠️ Windows PowerShell Users**: If you get an execution policy error:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4. Install Dependencies

**Option A: Minimal Install (Recommended for First Time)**

```bash
pip install -r requirements-minimal.txt
```

This installs all core features **except** NLP analysis (which requires additional setup).

**Option B: Full Install (Requires Visual C++ Build Tools)**

```bash
pip install -r requirements.txt
```

> **⚠️ Windows Users**: This requires [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). If you don't have it, use Option A.

### 5. Configure Environment

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` with your settings (see Configuration section below).

### 6. Initialize Database

```bash
python database_setup.py init
```

### 7. Run the Application

```bash
python run.py
```

✅ **Success!** Your backend should now be running at `http://localhost:5000`

---

## ⚙️ Configuration

### Google Cloud Setup (Required)

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project

2. **Enable APIs**
   - Navigate to "APIs & Services" → "Library"
   - Enable:
     - Google Drive API
     - Google OAuth2 API

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Authorized redirect URIs:
     ```
     http://localhost:5000/auth/google/callback
     http://127.0.0.1:5000/auth/google/callback
     ```
   - Save your Client ID and Client Secret

### Environment Variables (.env file)

```env
# ============================================
# Database Configuration
# ============================================
# Use SQLite for development (no setup needed)
DATABASE_URL=sqlite:///metadoc.db

# For production with MySQL:
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/metadoc_db

# ============================================
# Google OAuth2 (REQUIRED)
# ============================================
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# Optional: Service account for Drive API
# GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account-key.json

# ============================================
# Security (REQUIRED)
# ============================================
# Generate random strings for production
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# ============================================
# Institution Settings
# ============================================
ALLOWED_EMAIL_DOMAINS=cit.edu,yourdomain.edu
INSTITUTION_NAME=Cebu Institute of Technology - University

# ============================================
# Optional: AI Features
# ============================================
# GEMINI_API_KEY=your_gemini_api_key_here

# ============================================
# Application Settings
# ============================================
FLASK_ENV=development
FLASK_DEBUG=True
```

---

## 🔧 Optional: Enable NLP Features

If you installed with `requirements-minimal.txt`, the NLP module is disabled by default. To enable it:

### Windows Users

1. **Install Visual C++ Build Tools**
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "Desktop development with C++" workload
   - Restart your computer

2. **Install NLP Libraries**
   ```bash
   pip install spacy==3.6.1 nltk==3.8.1 textstat==0.7.3
   ```

3. **Download NLP Models**
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
   ```

4. **Enable NLP Module**
   
   Edit `app/__init__.py` and uncomment lines 110-112:
   
   ```python
   # Change from:
   # from app.modules.nlp import nlp_bp
   # app.register_blueprint(nlp_bp, url_prefix='/api/v1/nlp')
   
   # To:
   from app.modules.nlp import nlp_bp
   app.register_blueprint(nlp_bp, url_prefix='/api/v1/nlp')
   ```

5. **Restart the server**

### Linux/Mac Users

```bash
pip install spacy==3.6.1 nltk==3.8.1 textstat==0.7.3
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

Then uncomment the NLP module in `app/__init__.py` as shown above.

---

## 🐛 Troubleshooting

### Virtual Environment Issues

**Problem**: `pip` installs packages globally instead of in venv

**Solution**: Make sure you're using the venv's Python:
```bash
# Windows
.\venv\Scripts\python.exe -m pip install <package>

# Linux/Mac
./venv/bin/python -m pip install <package>
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'flask_jwt_extended'`

**Solution**: 
1. Ensure virtual environment is activated (you should see `(venv)` in your terminal)
2. Reinstall requirements:
   ```bash
   pip install -r requirements-minimal.txt
   ```

### SQLAlchemy Compatibility Error

**Problem**: `AssertionError` related to `SQLCoreOperations`

**Solution**: This is a Python 3.13 compatibility issue. Upgrade SQLAlchemy:
```bash
pip install --upgrade SQLAlchemy
```

### Google OAuth Errors

**Problem**: `Error 400: redirect_uri_mismatch`

**Solution**: 
- Check that redirect URI in `.env` exactly matches Google Cloud Console
- No trailing slashes
- Use exact protocol (http vs https)

**Problem**: `Error 403: access_denied`

**Solution**:
- Configure OAuth consent screen in Google Cloud Console
- Add test users if using external user type

### Database Errors

**Problem**: Database connection errors

**Solution for SQLite** (Development):
- No setup needed, file will be created automatically
- Make sure you have write permissions in the backend directory

**Solution for MySQL** (Production):
- Ensure MySQL server is running
- Verify credentials in DATABASE_URL
- Create database manually if needed:
  ```sql
  CREATE DATABASE metadoc_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```

---

## 📚 Additional Resources

- [Backend API Documentation](backend/README.md)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)

---

## 👥 Development Team

- Edgar B. Quiandao Jr.
- Paul G. Abellana  
- Miguel Ray A. Veloso
- Mark Christian Q. Garing

**Advisers**: Mr. Ralph Laviste & Dr. Cheryl Pantaleon

---

## 📝 Notes for Team Members

### First Time Setup Checklist

- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`requirements-minimal.txt`)
- [ ] `.env` file created and configured
- [ ] Google OAuth credentials obtained
- [ ] Database initialized
- [ ] Server running successfully

### Before Committing Code

- [ ] Virtual environment is activated
- [ ] All new dependencies added to `requirements.txt`
- [ ] `.env` file NOT committed (it's in `.gitignore`)
- [ ] Code tested locally
- [ ] No hardcoded credentials in code

### Common Commands

```bash
# Activate venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate      # Linux/Mac

# Install new package
pip install package-name
pip freeze > requirements.txt  # Update requirements

# Run server
python run.py

# Reset database
python database_setup.py init

# Deactivate venv
deactivate
```
