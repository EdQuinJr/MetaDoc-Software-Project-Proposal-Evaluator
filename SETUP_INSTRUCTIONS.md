# MetaDoc Backend Setup Instructions

**Last Updated**: December 21, 2025  
**Tested On**: Windows 11, Python 3.13

This guide provides step-by-step instructions for setting up the MetaDoc backend for development.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.10 to 3.13** (Download from [python.org](https://www.python.org/downloads/))
- **Git** (for cloning the repository)
- **Google Cloud Account** (for Unified OAuth, Drive API, and Gemini AI)
- **SQLite** (Default) or **PostgreSQL** (Recommended for Production)

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

### 6. Run the Application

```bash
python run.py
```

✅ **Success!** Your backend should now be running at `http://localhost:5000`

---

## ⚙️ Configuration

### Provider Configuration (REQUIRED)

#### 1. Google Cloud (Unified Authentication & API)
- **Enable APIs**: Drive API, Gemini AI API.
- **Create OAuth Client ID**: Type "Web application".
- **Redirect URIs**:
  ```
  http://localhost:5000/auth/google/callback
  http://localhost:5173/auth/callback
  ```
- **Gemini**: Obtain an API Key from [AI Studio](https://aistudio.google.com/).


### Environment Variables (.env file)

```env
# ============================================
# Database Configuration
# ============================================
# SQLite (Recommended for development - no setup needed)
# The backend automatically uses absolute path to avoid issues
DATABASE_URL=sqlite:///metadoc.db

# For production with MySQL:
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/metadoc_db

# For PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost:5432/metadoc_db

# ============================================
# Auth Configuration (REQUIRED)
# ============================================
# Google (Unified OAuth 2.0)
GOOGLE_CLIENT_ID=your_google_id
GOOGLE_CLIENT_SECRET=your_google_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# ============================================
# AI & Content (REQUIRED)
# ============================================
GEMINI_API_KEY=your_gemini_api_key_here

# ============================================
# File Storage & Limits
# ============================================
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_EMAIL_DOMAINS=cit.edu
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

**Problem**: `sqlite3.OperationalError: unable to open database file`

**Solution**:
- The backend now automatically handles database paths with absolute paths
- Database file will be created in `backend/metadoc.db`
- Ensure you have write permissions in the backend directory
- If using OneDrive, the path with spaces is handled automatically

**Problem**: Database connection errors with MySQL/PostgreSQL

**Solution**:
- Ensure database server is running
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

# Check database location (for debugging)
python -c "from config import config; print(config['development'].SQLALCHEMY_DATABASE_URI)"

# Deactivate venv
deactivate
```
