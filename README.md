# MetaDoc: Software Project Proposal Evaluator

MetaDoc is a comprehensive document analysis system designed for academic institutions to streamline document submission, metadata extraction, and automated evaluation of student proposals and papers.

## 🏗️ System Architecture

The system consists of:
- **Backend API**: Flask-based REST API with session-based authentication
- **Frontend**: React application with Vite and modern UI components
- **Database**: SQLite (development) / PostgreSQL (production)
- **Analysis Engine**: Document metadata extraction, NLP analysis, and heuristic evaluation
- **File Storage**: Local file system with organized directory structure

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+** and npm
- **SQLite** (included with Python)
- **Git** (for version control)
- **Windows/Linux/macOS** (cross-platform compatible)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd MetaDoc-Software-Project-Proposal-Evaluator
```

2. **Setup Backend**:
```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env file with your settings (see Configuration section)

# Initialize database
python scripts/reset_database.py

# Start server
python run.py
```

✅ Backend will be available at: `http://localhost:5000`

3. **Setup Frontend**:
```bash
cd frontend/metadoc

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend will be available at: `http://localhost:5173` or `http://localhost:5174`

4. **Create Test Account**:
```bash
# In backend directory with venv activated
python scripts/create_test_user.py
```

Default test credentials:
- **Email**: `professor@example.com`
- **Password**: `password`

## 📖 Detailed Documentation

For more information, see:

- **[🔧 Backend API Documentation](backend/README.md)** - API endpoints and services
- **[🎨 Frontend Documentation](frontend/metadoc/README.md)** - Component structure and styling
- **[📊 Database Schema](backend/app/models/)** - Data models and relationships

## ⚙️ Configuration

### Backend Configuration

Create `backend/.env` file:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production

# Database
DATABASE_URL=sqlite:///metadoc.db

# File Storage
UPLOAD_FOLDER=uploads
TEMP_STORAGE_PATH=temp
MAX_FILE_SIZE=52428800  # 50MB

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174

# Session Settings
SESSION_COOKIE_SECURE=False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### Frontend Configuration

The frontend uses Vite proxy configuration (no `.env` needed for development).

See `frontend/metadoc/vite.config.js` for proxy settings.

## 🎯 Key Features

### 📤 Submission Management
- **Token-based submission system** - Students submit via unique links
- **Deadline management** - Create and manage submission deadlines with descriptions
- **File validation** - Automatic DOCX file validation and size checking
- **Cascade delete protection** - Prevent accidental deletion of deadlines with submissions

### 📊 Document Analysis
- **Metadata extraction** - Author, creation date, last modified, last editor
- **Content statistics** - Word count, page count, character count, sentence count
- **Document properties** - Comprehensive metadata from DOCX files

### 👨‍🏫 Professor Dashboard
- **Overview statistics** - Active deadlines, total submissions, pending analysis
- **Folder view** - Organize submissions by deadline
- **Submission details** - View complete analysis results
- **Individual file management** - Delete specific submissions
- **Bulk operations** - Delete entire folders with all submissions

### 🔐 Authentication & Security
- **Session-based authentication** - Secure login system
- **User registration** - Email and password registration
- **Protected routes** - Role-based access control
- **Token validation** - Secure submission links with expiration

### 🎨 Modern UI/UX
- **Responsive design** - Works on desktop, tablet, and mobile
- **Clean interface** - Simple black icons, no clutter
- **Visual feedback** - Success messages and loading states
- **Smooth redirects** - Automatic navigation after actions

## 🔧 Development

### Project Structure

```
MetaDoc-Software-Project-Proposal-Evaluator/
├── backend/
│   ├── app/
│   │   ├── api/                    # API route handlers
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── dashboard.py       # Dashboard endpoints
│   │   │   ├── submission.py      # Submission endpoints
│   │   │   └── metadata.py        # Metadata endpoints
│   │   ├── services/              # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── submission_service.py
│   │   │   └── metadata_service.py
│   │   ├── models/                # Database models
│   │   │   ├── user.py
│   │   │   ├── submission.py
│   │   │   ├── deadline.py
│   │   │   └── analysis.py
│   │   ├── schemas/               # Data transfer objects
│   │   │   └── dto/
│   │   ├── core/                  # Core configurations
│   │   │   ├── extensions.py     # Flask extensions
│   │   │   └── config.py         # App configuration
│   │   └── utils/                 # Utility functions
│   ├── scripts/                   # Database and utility scripts
│   │   ├── reset_database.py
│   │   └── create_test_user.py
│   ├── uploads/                   # Uploaded files storage
│   ├── temp/                      # Temporary file storage
│   ├── requirements.txt           # Python dependencies
│   ├── run.py                     # Application entry point
│   └── metadoc.db                 # SQLite database (auto-created)
├── frontend/
│   └── metadoc/
│       ├── src/
│       │   ├── pages/             # Page components
│       │   │   ├── TokenBasedSubmission.jsx    # Public submission form
│       │   │   ├── AuthenticatedSubmission.jsx # Logged-in submission
│       │   │   ├── SubmissionDetailView.jsx    # Submission details
│       │   │   ├── Dashboard.jsx               # Professor dashboard
│       │   │   ├── Folder.jsx                  # Folder view
│       │   │   ├── Deadlines.jsx               # Deadline management
│       │   │   ├── Login.jsx                   # Login page
│       │   │   └── Register.jsx                # Registration page
│       │   ├── components/        # Reusable components
│       │   ├── services/          # API service layer
│       │   │   └── api.js
│       │   ├── contexts/          # React contexts
│       │   │   └── AuthContext.jsx
│       │   ├── styles/            # CSS stylesheets
│       │   └── App.jsx            # Main app component
│       ├── vite.config.js         # Vite configuration
│       └── package.json           # Node dependencies
└── README.md                      # This file
```

### Development Workflow

**Starting the Application:**

```bash
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate.ps1  # Windows
python run.py

# Terminal 2 - Frontend
cd frontend/metadoc
npm run dev
```

**Resetting the Database:**

```bash
cd backend
python scripts/reset_database.py
```

**Creating Test Users:**

```bash
cd backend
python scripts/create_test_user.py
```

## 🐛 Troubleshooting

### Backend Won't Start

**Issue**: `ModuleNotFoundError` or import errors

**Solution**: 
```bash
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend CORS Errors

**Issue**: `Failed to fetch` or CORS errors in browser console

**Solution**: 
1. Ensure backend is running on `http://localhost:5000`
2. Check `vite.config.js` proxy configuration
3. Clear browser cache and restart frontend

### Database Locked Error

**Issue**: `database is locked` error

**Solution**: 
```bash
# Close all Python processes
# On Windows Task Manager, end all python.exe processes
# Then restart the backend
```

### Port Already in Use

**Issue**: `Address already in use` error

**Solution**:
```bash
# Windows - Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Login Not Working

**Issue**: Login fails or session not persisting

**Solution**:
1. Clear browser cookies and localStorage
2. Check backend logs for errors
3. Verify user exists in database
4. Reset database and create new test user

## 📱 User Guide

### For Professors

1. **Register/Login**
   - Navigate to `http://localhost:5173`
   - Register with email and password
   - Login to access dashboard

2. **Create Deadline**
   - Go to "Deadline Management"
   - Click "Create New Deadline"
   - Fill in title, description, and deadline date
   - Click "Create Deadline"

3. **Generate Submission Link**
   - In deadline card, click "Generate Link"
   - Copy the submission link
   - Share with students

4. **View Submissions**
   - Go to "Folders"
   - Click on a deadline folder
   - View all submitted files
   - Click on a file to see detailed analysis

5. **Delete Submissions**
   - Click trash icon next to a file to delete it
   - Click folder delete to remove entire deadline (deletes all files inside)

### For Students

1. **Access Submission Link**
   - Click the link provided by your professor
   - You'll see the deadline title and description

2. **Submit Document**
   - Enter your Student ID and Name
   - Upload your DOCX file (max 50MB)
   - Click "Submit Document"
   - Save your Job ID for tracking

3. **Submission Requirements**
   - File must be in DOCX format
   - File size must be under 50MB
   - File must contain actual content (not empty)

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login-basic` - Login with email/password
- `POST /api/v1/auth/logout` - Logout current session
- `GET /api/v1/auth/validate` - Validate session
- `POST /api/v1/auth/generate-submission-token` - Generate submission link

### Dashboard
- `GET /api/v1/dashboard/overview` - Get dashboard statistics
- `GET /api/v1/dashboard/submissions` - List all submissions
- `GET /api/v1/dashboard/submissions/:id` - Get submission details
- `DELETE /api/v1/dashboard/submissions/:id` - Delete submission
- `GET /api/v1/dashboard/deadlines` - List deadlines
- `POST /api/v1/dashboard/deadlines` - Create deadline
- `PUT /api/v1/dashboard/deadlines/:id` - Update deadline
- `DELETE /api/v1/dashboard/deadlines/:id` - Delete deadline (and all submissions)

### Submission
- `GET /api/v1/submission/token-info` - Get deadline info from token
- `POST /api/v1/submission/upload` - Upload document
- `GET /api/v1/submission/status/:id` - Check submission status

### Metadata
- `GET /api/v1/metadata/result/:id` - Get analysis results

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
