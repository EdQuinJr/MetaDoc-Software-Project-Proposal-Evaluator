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
