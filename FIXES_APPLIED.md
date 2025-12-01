# Fixes Applied to MetaDoc

## Issue: 500 Internal Server Error

### Root Cause
The backend was trying to access `current_app.config` during module import time, before the Flask application context was available. This caused the `AuthenticationService` initialization to fail.

### Fixes Applied

#### 1. Backend - Auth Module (`backend/app/modules/auth.py`)
- **Changed**: Lazy initialization of `AuthenticationService`
- **Before**: `auth_service = AuthenticationService()` at module level
- **After**: 
  ```python
  auth_service = None
  
  def get_auth_service():
      global auth_service
      if auth_service is None:
          auth_service = AuthenticationService()
      return auth_service
  ```
- **Updated**: All route handlers to use `get_auth_service()` instead of `auth_service`

#### 2. Backend - Dashboard Module (`backend/app/modules/dashboard.py`)
- **Changed**: Import statement
- **Before**: `from app.modules.auth import auth_service`
- **After**: `from app.modules.auth import get_auth_service`
- **Updated**: Authentication decorator to use `get_auth_service().validate_session()`

#### 3. Frontend - Submit Document (`frontend/metadoc/src/pages/SubmitDocument.jsx`)
- **Fixed**: React hook error
- **Before**: `useState(() => { fetchDeadlines(); }, [])`
- **After**: `useEffect(() => { fetchDeadlines(); }, [])`
- **Added**: Missing `useEffect` import

#### 4. Frontend - Vite Configuration (`frontend/metadoc/vite.config.js`)
- **Added**: Proxy configuration for API requests
  ```javascript
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
  ```

#### 5. Frontend - API Service (`frontend/metadoc/src/services/api.js`)
- **Changed**: API base URL to use relative path
- **Before**: `const API_BASE_URL = 'http://localhost:5000/api/v1'`
- **After**: `const API_BASE_URL = '/api/v1'`
- This leverages the Vite proxy to avoid CORS issues

#### 6. Frontend - Environment Variables (`.env`)
- **Updated**: API base URL
- **Before**: `VITE_API_BASE_URL=http://localhost:5000/api/v1`
- **After**: `VITE_API_BASE_URL=/api/v1`

## How to Test

### 1. Restart Backend
```bash
cd backend
python run.py
```

### 2. Restart Frontend
```bash
cd frontend/metadoc
npm run dev
```

### 3. Access Application
Open browser to `http://localhost:5173`

## Expected Behavior

- ✅ No more 500 Internal Server Error
- ✅ Login page loads correctly
- ✅ API requests work through Vite proxy
- ✅ No CORS errors
- ✅ Backend initializes without errors

## Additional Notes

### Why Lazy Initialization?
Flask's `current_app` is only available within an application context. When modules are imported, the app context doesn't exist yet. Lazy initialization ensures the service is only created when it's actually needed (during a request), when the app context is available.

### Why Vite Proxy?
During development, the frontend (port 5173) and backend (port 5000) run on different ports. This causes CORS issues. The Vite proxy forwards API requests from the frontend to the backend, making them appear to come from the same origin.

### Production Deployment
For production:
1. Build the frontend: `npm run build`
2. Serve the `dist` folder with a web server
3. Update `VITE_API_BASE_URL` to the production backend URL
4. Configure backend CORS to allow the production frontend domain

## Files Modified

### Backend
- `backend/app/modules/auth.py`
- `backend/app/modules/dashboard.py`

### Frontend
- `frontend/metadoc/src/pages/SubmitDocument.jsx`
- `frontend/metadoc/vite.config.js`
- `frontend/metadoc/src/services/api.js`
- `frontend/metadoc/.env`

## Status
✅ All fixes applied and tested
✅ Backend starts without errors
✅ Frontend connects to backend successfully
✅ No more 500 errors
