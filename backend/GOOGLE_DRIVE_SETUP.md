# Google Drive Integration Setup Guide

## Problem
Google Drive link submissions are failing with "Unexpected error occurred"

## Solution Steps

### 1. Check Google Drive API Configuration

The app needs Google Drive API credentials. Check if you have:

**File**: `backend/credentials/google-credentials.json`

If missing, you need to:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Drive API**
4. Create **Service Account** credentials
5. Download JSON key file
6. Save as `google-credentials.json` in `backend/credentials/` folder

### 2. Share Google Drive Files Properly

For the link to work, the file must be shared:

**Option A: Anyone with the link**
1. Right-click file in Google Drive
2. Click "Share"
3. Change to "Anyone with the link"
4. Set permission to "Viewer" or "Commenter"
5. Copy link

**Option B: Share with service account**
1. Get service account email from credentials JSON
2. Share file with that email address
3. Set permission to "Viewer"

### 3. Valid Link Formats

The system accepts these formats:
- `https://docs.google.com/document/d/FILE_ID/edit`
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/open?id=FILE_ID`

### 4. Test Without Google Drive API

If you don't have API access, you can:
1. Download the file from Google Drive manually
2. Use the **File Upload** tab instead
3. Upload the downloaded .docx file

### 5. Check Backend Logs

After trying to submit, check the backend terminal for detailed error messages. The error will now show:
```
Drive link submission error: [specific error]
Traceback: [full error details]
```

Common errors:
- `403 Forbidden` → File not shared properly
- `404 Not Found` → Invalid file ID or file deleted
- `No credentials` → Google API not configured
- `Invalid link format` → Link format not recognized

### 6. Alternative: Disable Google Drive Feature

If you don't need Google Drive integration, you can:
1. Remove the "Google Drive Link" tab from the UI
2. Only use file upload functionality
3. This works without any API configuration

## Quick Fix for Development

If you just want to test the system without Google Drive:

1. **Use File Upload Only**
   - Click "File Upload" tab
   - Upload .docx files directly
   - This works immediately without any setup

2. **Mock Google Drive** (for testing)
   - The system will show the error
   - But file upload will work perfectly

## Need Help?

Check the backend logs when you click "Submit Link" - the new error logging will show exactly what's wrong!
