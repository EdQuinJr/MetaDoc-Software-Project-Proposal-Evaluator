# MetaDoc: Software Project Proposal Evaluator

MetaDoc is a Google Drive-integrated metadata analyzer for academic document evaluation, designed to enhance the fairness, transparency, and efficiency of academic document assessment within IT and Computer Science programs.

## 🏗️ System Overview

The system consists of:
- **Backend API**: Flask-based REST API with Google OAuth2 integration
- **Frontend**: React application with responsive design
- **Database**: MySQL/SQLite for data storage
- **Google Integration**: Drive API and OAuth2 authentication

## 🚀 Complete Setup Guide

### Prerequisites

- Python 3.10+
- Node.js 18+
- MySQL Server (or use SQLite for development)
- Google Cloud Project

### Step 1: Google Cloud Console Setup

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Required APIs**:
   - Google Drive API
   - Google OAuth2 API
   - Go to "APIs & Services" → "Library" and enable both

3. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Web application"
   - Add these Authorized redirect URIs:
     - `http://localhost:5000/auth/google/callback`
     - `http://127.0.0.1:5000/auth/google/callback`
   - Save the Client ID and Client Secret

4. **Create Service Account** (Optional for Drive access):
   - Go to "IAM & Admin" → "Service Accounts"
   - Create service account and download JSON key

### Step 2: Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

5. **Edit .env file with your credentials**:
```env
# Database (Choose one)
DATABASE_URL=sqlite:///metadoc.db  # For development
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/metadoc_db  # For production

# Google OAuth2 (Required)
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# Security
SECRET_KEY=your_super_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Institution Settings
ALLOWED_EMAIL_DOMAINS=cit.edu,school.edu.ph
INSTITUTION_NAME=Your Institution Name
```

6. **Setup database**:
```bash
python database_setup.py init
```

7. **Download NLP models**:
```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

8. **Start backend server**:
```bash
python run.py
```

Backend will be available at: `http://localhost:5000`

### Step 3: Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend/metadoc
```

2. **Install dependencies**:
```bash
npm install
```

3. **Create environment file**:
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

4. **Configure frontend environment**:
```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
VITE_GOOGLE_CLIENT_ID=your_client_id_here
```

5. **Start frontend development server**:
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 🔧 Troubleshooting

### Google OAuth Errors

**Error 400: redirect_uri_mismatch**
- Ensure redirect URIs are properly configured in Google Cloud Console
- Check that the URI in .env matches exactly with Google Console

**Database Connection Errors**
- For MySQL: Ensure MySQL server is running and credentials are correct
- For SQLite: No additional setup needed, database file will be created automatically

**Import Errors**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

## 📱 Usage

1. **Access the application**: `http://localhost:3000`
2. **Login with Google**: Use institutional email (@cit.edu)
3. **Submit documents**: Upload files or provide Google Drive links
4. **View analysis**: Check dashboard for insights and reports

## 🏫 Institution Configuration

Update the `.env` file with your institution settings:
```env
ALLOWED_EMAIL_DOMAINS=yourdomain.edu,anotherdomain.edu.ph
INSTITUTION_NAME=Your Institution Name
```

## 📚 Documentation

- [Backend API Documentation](backend/README.md)
- [Frontend Documentation](frontend/metadoc/README.md)
- [Setup Guide](SETUP_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md) 
