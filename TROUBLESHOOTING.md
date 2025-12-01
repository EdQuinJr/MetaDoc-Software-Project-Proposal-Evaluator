# MetaDoc Troubleshooting Guide

## Common Issues and Solutions

### 500 Internal Server Error

**Problem:** Frontend shows "500 Internal Server Error" when making API requests.

**Solutions:**

1. **Check Backend is Running**
   ```bash
   cd backend
   python run.py
   ```
   Backend should be running on `http://localhost:5000`

2. **Verify Database Connection**
   - Check `.env` file has correct `DATABASE_URL`
   - Ensure database server is running
   - Run database migrations:
     ```bash
     python database_setup.py
     ```

3. **Check Backend Logs**
   - Look at terminal where backend is running
   - Check for Python errors or missing dependencies

4. **Install Missing Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### CORS Errors

**Problem:** Browser console shows CORS policy errors.

**Solutions:**

1. **Use Vite Proxy (Development)**
   - The Vite config already includes proxy settings
   - Ensure `.env` uses relative URL: `VITE_API_BASE_URL=/api/v1`
   - Restart Vite dev server after changing .env

2. **Backend CORS Configuration**
   - Backend already has CORS enabled in `app/__init__.py`
   - Verify allowed origins include your frontend URL

### Authentication Errors

**Problem:** Login fails or redirects don't work.

**Solutions:**

1. **Google OAuth Not Configured**
   - Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in backend `.env`
   - Configure redirect URI in Google Cloud Console
   - Ensure redirect URI matches: `http://localhost:5000/api/v1/auth/callback`

2. **Email Domain Restriction**
   - Check `ALLOWED_EMAIL_DOMAINS` in backend `.env`
   - Add your email domain: `ALLOWED_EMAIL_DOMAINS=cit.edu,gmail.com`

3. **Session Token Issues**
   - Clear browser localStorage
   - Try logging in again

### Frontend Build Errors

**Problem:** `npm install` or `npm run dev` fails.

**Solutions:**

1. **Node Version**
   ```bash
   node --version  # Should be 18+
   ```

2. **Clear and Reinstall**
   ```bash
   cd frontend/metadoc
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Missing Dependencies**
   - Ensure `package.json` includes all required packages
   - Run `npm install` again

### API Connection Errors

**Problem:** Frontend can't connect to backend API.

**Solutions:**

1. **Check API URL**
   - Development: Use `/api/v1` (relative URL with proxy)
   - Production: Use full URL like `https://api.example.com/api/v1`

2. **Verify Proxy Configuration**
   - Check `vite.config.js` has proxy settings
   - Restart Vite dev server

3. **Network Issues**
   - Ensure backend is accessible
   - Check firewall settings
   - Try accessing `http://localhost:5000/api/v1/auth/login` directly

### Database Errors

**Problem:** Backend crashes with database errors.

**Solutions:**

1. **Create Database Tables**
   ```bash
   cd backend
   python database_setup.py
   ```

2. **Check Database Connection**
   - Verify `DATABASE_URL` in `.env`
   - Test database connection manually
   - For SQLite: ensure file path is correct
   - For MySQL/PostgreSQL: ensure server is running

3. **Migration Issues**
   ```bash
   flask db stamp head
   flask db migrate
   flask db upgrade
   ```

### File Upload Errors

**Problem:** File uploads fail or return errors.

**Solutions:**

1. **Check Upload Directories**
   - Ensure `uploads/`, `temp_files/`, `reports/` directories exist
   - Backend creates these automatically, but check permissions

2. **File Size Limit**
   - Default is 50MB (`MAX_CONTENT_LENGTH=52428800`)
   - Increase in backend `.env` if needed

3. **File Type Validation**
   - Only DOCX and DOC files are supported
   - Check file extension and MIME type

### Google Drive Integration Errors

**Problem:** Google Drive link submission fails.

**Solutions:**

1. **Service Account Not Configured**
   - Create service account in Google Cloud Console
   - Download JSON key file
   - Set `GOOGLE_SERVICE_ACCOUNT_FILE` in backend `.env`

2. **Permission Denied**
   - File must be shared with "Anyone with the link"
   - Or add service account email to file permissions

3. **Invalid Link Format**
   - Use full Google Drive URL
   - Supported formats:
     - `https://drive.google.com/file/d/FILE_ID`
     - `https://docs.google.com/document/d/FILE_ID`

## Development Tips

### Hot Reload Not Working

1. **Frontend:**
   - Restart Vite dev server
   - Clear browser cache
   - Check for syntax errors

2. **Backend:**
   - Ensure `FLASK_ENV=development` in `.env`
   - Flask auto-reloads on file changes
   - Check for Python syntax errors

### Debugging API Calls

1. **Browser DevTools**
   - Open Network tab
   - Filter by "XHR" or "Fetch"
   - Check request/response details

2. **Backend Logs**
   - Watch terminal output
   - Enable debug logging: `LOG_LEVEL=DEBUG`

3. **API Testing**
   - Use Postman or curl to test endpoints
   - Example:
     ```bash
     curl http://localhost:5000/api/v1/auth/login
     ```

### Environment Variables Not Loading

1. **Frontend (.env)**
   - Must start with `VITE_`
   - Restart dev server after changes
   - Access via `import.meta.env.VITE_VARIABLE_NAME`

2. **Backend (.env)**
   - Use `python-dotenv` (already installed)
   - Restart backend after changes
   - Access via `os.environ.get('VARIABLE_NAME')`

## Getting Help

If issues persist:

1. Check backend terminal for error messages
2. Check browser console for frontend errors
3. Review the SRS document for requirements
4. Check `SETUP_GUIDE.md` for configuration steps
5. Verify all environment variables are set correctly

## Quick Reset

If everything is broken, try a complete reset:

```bash
# Backend
cd backend
rm -rf __pycache__ *.db
python database_setup.py
python run.py

# Frontend (new terminal)
cd frontend/metadoc
rm -rf node_modules package-lock.json .vite
npm install
npm run dev
```

Then access `http://localhost:5173` in your browser.
