# MetaDoc Frontend

React-based frontend for MetaDoc: Google Drive-Integrated Metadata Analyzer for Academic Document Evaluation.

## Features

- **Maroon & Gold Theme** - CIT-U branded color scheme
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Google OAuth Authentication** - Secure institutional login
- **Document Submission** - File upload and Google Drive link support
- **Dashboard Analytics** - Overview of submissions and insights
- **Detailed Reports** - View metadata, NLP analysis, and heuristic insights
- **Clean UI Components** - Cards, badges, forms with consistent styling

## Tech Stack

- React 19
- React Router v6
- Axios for API calls
- Lucide React for icons
- Vite for build tooling

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:5000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Update `.env` with your backend URL:
```
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

### Development

1. **Ensure backend is running** on `http://localhost:5000`

2. **Start development server**:
```bash
npm run dev
```

3. **Access the application**:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:5000`

### Build for Production

```bash
npm run build
npm run preview
```

## 🔧 Troubleshooting

### Common Issues

**CORS Errors**
- Ensure backend is running on `http://localhost:5000`
- Check VITE_API_BASE_URL in .env matches backend URL
- Backend CORS should allow `http://localhost:3000`

**Google OAuth Issues**
- Verify VITE_GOOGLE_CLIENT_ID matches backend GOOGLE_CLIENT_ID
- Check Google Console has correct redirect URIs configured
- Ensure OAuth consent screen is properly configured

**API Connection Errors**
- Check if backend server is running: `curl http://localhost:5000/health`
- Verify .env file has correct VITE_API_BASE_URL
- Check browser Network tab for failed requests

**Build Errors**
- Clear node_modules: `rm -rf node_modules package-lock.json && npm install`
- Check Node.js version: `node --version` (should be 18+)
- Update dependencies: `npm update`

### Environment Variables

Create `.env` file with these variables:
```env
# Required
VITE_API_BASE_URL=http://localhost:5000/api/v1
VITE_GOOGLE_CLIENT_ID=your_google_client_id

# Optional
VITE_APP_NAME=MetaDoc
VITE_INSTITUTION_NAME=Your Institution
VITE_DEBUG=true
```

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Layout/         # Layout components
├── contexts/           # React contexts
│   └── AuthContext.jsx # Authentication context
├── pages/              # Page components
│   ├── Dashboard.jsx   # Main dashboard
│   ├── Login.jsx       # Login page
│   ├── Submissions.jsx # Submissions list
│   └── ...
├── services/           # API services
│   └── api.js         # Axios configuration
├── App.jsx            # Main App component
└── main.jsx           # Entry point
```

## 🌐 Configuration

### Authentication Flow

1. User clicks "Login with Google"
2. Redirected to Google OAuth
3. After approval, redirected to backend `/auth/google/callback`
4. Backend validates and creates session
5. Frontend receives auth token
6. Token stored in localStorage for API requests

### API Integration

The frontend communicates with backend via REST API:
- Authentication: `/api/v1/auth/*`
- Submissions: `/api/v1/submissions/*`
- Dashboard: `/api/v1/dashboard/*`
- Reports: `/api/v1/reports/*`

### Styling

- **Theme**: Maroon & Gold (CIT-U colors)
- **Framework**: Custom CSS with CSS Variables
- **Responsive**: Mobile-first approach
- **Icons**: Lucide React

## 🚀 Deployment

### Development
```bash
npm run dev    # Start dev server
npm run build  # Build for production
npm run preview # Preview production build
```

### Production

1. **Build the application**:
```bash
npm run build
```

2. **Deploy static files**:
   - Upload `dist/` folder to web server
   - Configure web server for SPA routing
   - Set proper environment variables

3. **Update environment for production**:
```env
VITE_API_BASE_URL=https://your-backend-domain.com/api/v1
VITE_GOOGLE_CLIENT_ID=your_production_client_id
```

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Google OAuth2 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Backend API Documentation](../../backend/README.md)

Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── components/
│   └── Layout/
│       ├── DashboardLayout.jsx
│       └── DashboardLayout.css
├── contexts/
│   └── AuthContext.jsx
├── pages/
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   ├── Submissions.jsx
│   ├── SubmissionDetail.jsx
│   └── SubmitDocument.jsx
├── services/
│   └── api.js
├── App.jsx
├── main.jsx
└── index.css
```

## Color Scheme

- **Primary Maroon**: `#800020`
- **Gold**: `#FFD700`
- **White Background**: `#FFFFFF`
- **Gray Accents**: Various shades for text and borders

## API Integration

The frontend connects to the backend API endpoints:

- `/api/v1/auth/*` - Authentication
- `/api/v1/submission/*` - File submissions
- `/api/v1/dashboard/*` - Dashboard data
- `/api/v1/metadata/*` - Metadata analysis
- `/api/v1/insights/*` - Heuristic insights
- `/api/v1/nlp/*` - NLP analysis
- `/api/v1/reports/*` - Report exports

## License

 2025 MetaDoc - Cebu Institute of Technology University

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).
## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
