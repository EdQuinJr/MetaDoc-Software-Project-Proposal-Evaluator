# MetaDoc Setup Guide

## Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL/MariaDB (XAMPP recommended)
- Google Cloud Platform account

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

Edit `.env` and configure:

#### Database
```env
DATABASE_URL=mysql+pymysql://root:@localhost:3306/metadoc_db
```

#### Google OAuth 2.0
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Drive API**
4. Go to **APIs & Services** → **Credentials**
5. Create **OAuth 2.0 Client ID** (Web application)
6. Add authorized redirect URIs:
   - `http://localhost:5000/api/v1/auth/callback`
7. Add authorized JavaScript origins:
   - `http://localhost:3000`
8. Copy Client ID and Client Secret to `.env`:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/v1/auth/callback
```

#### Google Drive Service Account
1. In Google Cloud Console, go to **APIs & Services** → **Credentials**
2. Create **Service Account**
3. Download JSON key file
4. Save as `backend/credentials/google-credentials.json`
5. Update `.env`:

```env
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/google-credentials.json
```

#### Security Keys
Generate random keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Update `.env`:
```env
SECRET_KEY=your-generated-secret-key
JWT_SECRET_KEY=your-generated-jwt-key
```

#### Email Domains
```env
ALLOWED_EMAIL_DOMAINS=gmail.com,cit.edu
# Leave empty to allow all domains
```

### 3. Create Database

```bash
# Using MySQL Workbench or command line
CREATE DATABASE metadoc_db;
```

Or use the helper script:
```bash
python create_db.py
```

### 4. Initialize Database Tables

```bash
python reset_db.py
```

### 5. Run Backend Server

```bash
python run.py
```

Backend will run on: `http://localhost:5000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend/metadoc
npm install
```

### 2. Configure API URL

Edit `src/services/api.js` if needed (default: `http://localhost:5000`)

### 3. Run Frontend

```bash
npm start
```

Frontend will run on: `http://localhost:3000`

## Testing the Application

### 1. Login
- Go to `http://localhost:3000`
- Click "Sign in with Google"
- Login with allowed email domain

### 2. Create Deadline
- Go to Deadlines page
- Create a new deadline
- Generate submission token

### 3. Submit Document
- Use the submission token link
- Upload a DOCX file or provide Google Drive link
- Enter student ID (e.g., "22-1686-452")

### 4. View Analysis
- Go to Files page
- Click on submission to view details
- See metadata, statistics, and contributors

## Google Drive Link Submission

For Google Drive links to work:

1. **File must be shared**:
   - Right-click file in Google Drive
   - Click "Share"
   - Set to "Anyone with the link can view"

2. **Valid link formats**:
   - `https://docs.google.com/document/d/FILE_ID/edit`
   - `https://drive.google.com/file/d/FILE_ID/view`

## Troubleshooting

### Database Connection Error
- Make sure MySQL is running (XAMPP)
- Check database credentials in `.env`
- Verify database exists: `SHOW DATABASES;`

### Google Login Error
- Check Client ID and Secret are correct
- Verify redirect URI matches in Google Console
- Make sure email domain is in `ALLOWED_EMAIL_DOMAINS`

### Google Drive Error
- Check service account credentials file exists
- Verify file is shared properly
- Check backend logs for detailed error

## File Structure

```
MetaDoc/
├── backend/
│   ├── app/
│   ├── credentials/
│   │   └── google-credentials.json  # Add this
│   ├── uploads/                      # Created automatically
│   ├── .env                          # Create from .env.example
│   ├── .env.example
│   └── run.py
├── frontend/
│   └── metadoc/
│       ├── src/
│       └── package.json
└── SETUP.md
```

## Security Notes

**Never commit these files to Git:**
- `.env`
- `credentials/google-credentials.json`
- `uploads/*`
- `*.db`

These are already in `.gitignore`.

## Support

For issues, check:
- Backend logs in terminal
- Browser console (F12)
- Database logs in MySQL
