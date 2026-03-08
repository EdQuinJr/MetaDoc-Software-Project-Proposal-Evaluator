# MetaDoc: Software Project Proposal Evaluator - Final System Summary

## 🎉 Project Status: COMPLETE & PRODUCTION READY

**Last Updated:** March 8, 2026  
**Backend URL:** `http://localhost:5000`  
**Frontend URL:** `http://localhost:5173`  
**Status:** ✅ Fully Functional & Optimized

---

## 📊 Project Overview
MetaDoc is an advanced document analysis and evaluation system designed for academic institutions. It streamlines the submission process for student proposals, provides automated metadata extraction, performs deep NLP analysis, and leverages Gemini AI for qualitative insights.

### Major Achievements:
- ✅ **Unified Authentication:** Secure login via Google/Gmail OAuth.
- ✅ **Whitelist Gatekeeping:** Integration with **Class Records** to authorize specific students.
- ✅ **Robust Identity Deduplication:** Smart merging of document contributors via name/email normalization.
- ✅ **Tiered Service Architecture:** Clean separation of concerns with 3-layer Backend and Component-based Frontend.
- ✅ **AI-Powered Insights:** Qualitative evaluation based on custom **Rubrics** using Google Gemini.
- ✅ **Google Drive Integration:** Direct link submission with guided permission handling.

---

## 🏗️ System Architecture

### 🛡️ Backend (3-Layer Modular)
The backend follows a domain-driven design with clear separation between the API, Business Logic, and Persistence layers.

```
┌─────────────────────────────────────────┐
│  API Layer (Controllers/Blueprints)     │
│  - Thin route handlers & DTO mapping    │
│  - Authentication & Role-based access   │
└─────────────────────────────────────────┘
           ↓ calls services
┌─────────────────────────────────────────┐
│  Service Layer (Business Logic)         │
│  - 12 Specialized Service Classes       │
│  - Independent of HTTP/Framework        │
└─────────────────────────────────────────┘
           ↓ uses models
┌─────────────────────────────────────────┐
│  Persistence Layer (SQLAlchemy ORM)     │
│  - Domain Models & Relationships        │
│  - SQLite/PostgreSQL support            │
└─────────────────────────────────────────┘
```

### 🎨 Frontend (Component-Based React)
Powered by Vite and React, the frontend provides a high-performance, responsive dashboard.

```
┌─────────────────────────────────────────┐
│  View Layer (Pages & Components)        │
│  - Responsive Tailwind/Vanilla CSS UI   │
│  - Real-time feedback & Loading states  │
└─────────────────────────────────────────┘
           ↓ uses hooks/context
┌─────────────────────────────────────────┐
│  State & Logic Layer (Context/Services) │
│  - AuthContext (Session Management)     │
│  - API Service (Axios Interceptors)     │
└─────────────────────────────────────────┘
```

---

## 📂 Comprehensive File Structure (Detailed View)

### 🛡️ Backend Structure
```text
backend/
├── app/
│   ├── api/                    # API Route Handlers
│   │   ├── auth.py             # Authentication & OAuth Logic
│   │   ├── dashboard.py        # Statistics & Management
│   │   ├── submission.py       # Uploads & Drive integration
│   │   ├── metadata.py         # Metadata extraction API
│   │   ├── insights.py         # Gemini AI & Heuristics
│   │   ├── nlp.py              # SpaCy NLP analysis
│   │   ├── reports.py          # PDF/CSV Export API
│   │   └── rubric.py           # Evaluation Rubric management
│   ├── services/               # Scalable Service Layer
│   │   ├── auth_service.py     # Session & OAuth Logic
│   │   ├── dashboard_service.py# Data aggregation
│   │   ├── metadata_service.py # Extraction & Processing
│   │   ├── nlp_service.py      # Readability & Text analysis
│   │   ├── drive_service.py    # Google API authentication
│   │   └── identity_service.py # [NEW] Deduplication & Normalization
│   ├── models/                 # Database Relationships
│   │   ├── user.py, student.py # Identity & Whitelist models
│   │   ├── deadline.py, rubric.py# Goal & Evaluation models
│   │   └── submission.py       # Tracking & Result models
│   └── core/                   # Centralized Infrastructure (Extensions, Config)
├── scripts/                    # Admin Tools (Reset DB, Create Superuser)
└── run.py                      # Application Entry Point
```

### 🎨 Frontend Structure
```text
frontend/metadoc/src/
├── pages/                      # Main Application Screens
│   ├── Dashboard.jsx           # Core Stats & Navigation
│   ├── ClassRecord.jsx         # Whitelist Management & Upload
│   ├── Deadlines.jsx           # Date & Hard/Soft rules
│   ├── Folder.jsx              # Submission organization
│   ├── SubmissionDetailView.jsx# Deep analysis & AI report
│   ├── Login.jsx, Register.jsx # Professor Auth pages
│   └── TokenBasedSubmission.jsx# Student-facing submission form
├── components/                 # Reusable UI Blocks
│   ├── Layout/                 # Structural Components
│   │   └── DashboardLayout.jsx # Master Layout with Sidebar/Nav
│   └── common/                 # Atomic UI Components
│       ├── Button/, Card/      # Styled UI primitives
│       ├── Table/, Badge/      # Data display components
│       ├── Modal/, Input/      # Interaction components
│       └── SearchBar/          # List filtering logic
├── services/                   # Frontend Logic
│   └── api.js                  # Axios Instance & API methods
├── contexts/                   # Shared Global State
│   └── AuthContext.jsx         # Auth persistence & User status
└── styles/                     # Visual Design System
    ├── index.css               # Global Reset & Variables
    └── [Component].css         # Scoped component styling
```

---

## 🔑 Key Features & New Updates

### 1. 📂 Submission & Whitelisting (NEW)
- **Unified Authentication:** Students and Professors log in via secure Google OAuth.
- **Class Record Gatekeeping:** Only students pre-registered in the **Class Record** for a specific deadline can submit.
- **Identity Deduplication:** Normalizes author/editor names and emails to prevent duplicate profiles in reports.

### 2. 🤖 Analysis Engine
- **Metadata Extraction:** Extracts Authors, Creation Date, Revision Count, and Editing Time from DOCX XML.
- **NLP Analysis:** Readability scores (Flesch-Kincaid), Sentiment analysis, and Named Entity Recognition (NER).
- **Gemini AI Insights:** Context-specific summaries and evaluations based on Professor-defined **Rubrics**.

### 3. 👨‍🏫 Professor Tools
- **Dashboard Overview:** Real-time stats on active deadlines and pending submissions.
- **Folder Management:** Batch operations for organizing and deleting submissions.
- **Rubric Builder:** Create and manage custom evaluation criteria (Clarity, Contribution, etc.).
- **Report Generation:** Export comprehensive PDF/CSV reports with deduplicated identity data.

---

## 🚀 API Endpoints Consolidated

| Category | Endpoint | Method | Description |
|:--- |:--- |:---:|:--- |
| **Auth** | `/api/v1/auth/login-basic` | POST | Admin/Professor login |
| | `/api/v1/auth/validate` | GET | Session validation |
| | `/api/v1/auth/logout` | POST | User logout |
| **Dashboard**| `/api/v1/dashboard/overview` | GET | System-wide statistics |
| | `/api/v1/dashboard/deadlines` | POST | Create new deadline |
| | `/api/v1/dashboard/students` | GET | View/Manage Class Records |
| **Submission**| `/api/v1/submission/drive-link` | POST | Submit Google Drive document |
| | `/api/v1/submission/status/:id` | GET | Track analysis progress |
| **Analysis** | `/api/v1/insights/analyze/:id` | POST | Trigger Gemini AI analysis |
| | `/api/v1/metadata/result/:id` | GET | Fetch extracted metadata |
| **Rubrics** | `/api/rubrics/` | POST | Create custom evaluation rubric |

---

## 🔧 Technology Stack

### Backend
- **Core:** Flask (Python 3.13)
- **Database:** SQLAlchemy (ORM), SQLite
- **Security:** Flask-JWT-Extended, OAuth 2.0
- **AI/NLP:** Google Gemini (Generative AI), SpaCy, Textstat
- **Reports:** ReportLab (PDF), Pandas (CSV)

### Frontend
- **Framework:** React 18+ (Vite)
- **Styling:** CSS3, Modern UI Aesthetics
- **State:** React Context API
- **HTTP:** Axios with Interceptors
- **Auth:** Google OAuth 2.0

---

## ✅ Quality & Best Practices
- [x] **Zero Breaking Changes** during major refactoring.
- [x] **Secure File Handling** with size and type validation (Magic bytes).
- [x] **SQL Injection Prevention** via ORM parameterization.
- [x] **Responsive UI** tested on Chrome, Edge, and Mobile.
- [x] **Comprehensive Logging** for audit trails and debugging.

---

## 🎯 Conclusion
MetaDoc has evolved into a robust, scalable, and secure platform. With the integration of **Unified Google Auth**, **Identity Deduplication**, and **Automated Rubric Evaluation**, it provides a professional-grade solution for academic document management and evaluation.

**STATUS: READY FOR PRODUCTION DEPLOYMENT** ✅
