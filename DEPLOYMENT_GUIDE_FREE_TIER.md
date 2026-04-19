# MetaDoc Free-Tier Deployment Guide

Deploying MetaDoc completely on free-tier services is highly achievable and provides robust infrastructure for an academic project. This guide maps out the deployment using three of the most powerful and generous free limits out there:

1. **Supabase PostgreSQL** (Database)
2. **Render Web Service** (Backend)
3. **Vercel** (Frontend)

---

## 🛠 Prerequisites
- Accounts on [GitHub](https://github.com), [Neon](https://neon.tech/), [Render](https://render.com), and [Vercel](https://vercel.com).
- Your repository pushed to GitHub.

---

## Phase 1: Database (Supabase.com)

Supabase provides a generous free tier for PostgreSQL, complete with a beautiful dashboard. It's a perfect fit for your SQLAlchemy backend (and way more reliable than SQLite on ephemeral storage).

1. Go to [Supabase](https://supabase.com) and create a free account.
2. Click **New Project**, name it something like `metadoc-db` and set a secure database password.
3. Choose the region closest to your users and click Create.
4. From the Dashboard, go to **Project Settings** (gear icon) -> **Database**.
5. Scroll down to **Connection String** and tap the **URI** tab. 
6. Copy the connection string (it will look like `postgresql://postgres.[ref]:[password]@aws-0-region.pooler.supabase.com:6543/postgres`). 
7. *Replace `[password]` with the actual password you set in step 2.* **Save this for Phase 2.**

---

## Phase 2: Backend Deployment (Render.com)

Render makes deploying Flask apps extremely straightforward while providing free automated SSL and HTTPS.

1. Go to [Render](https://dashboard.render.com/) and click **New → Web Service**.
2. Connect your GitHub account and select your `MetaDoc-Software-Project-Proposal-Evaluator` repository.
3. Use the following configuration settings:
   - **Name**: `metadoc-api`
   - **Root Directory**: `backend` (very important!)
   - **Environment**: `Python`
   - **Region**: Choose the same region as your Supabase database if possible.
   - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
   - *(Note: If you haven't set up Flask-Migrate fully or prefer the script reset approach for the first build, use: `pip install -r requirements.txt && python scripts/reset_database.py`)*
   - **Start Command**: `gunicorn wsgi:app`
   - **Instance Type**: `Free`
4. Under **Environment Variables**, click **"Add Environment Variable"** and populate:
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`
   - `DATABASE_URL`: *(paste the Supabase connection string from Phase 1)*
   - `SECRET_KEY`: *(put a random secure string)*
   - `JWT_SECRET_KEY`: *(put a random secure string)*
   - `GOOGLE_CLIENT_ID`: *(from your Google Cloud Console)*
   - `GOOGLE_CLIENT_SECRET`: *(from your Google Cloud Console)*
   - `GEMINI_API_KEY`: *(from Google AI Studio)*
   - `CORS_ORIGINS`: `https://YOUR-FRONTEND-URL.vercel.app` *(update this after creating the Vercel app in Phase 3)*
5. Under **Secret Files** (if you're using a JSON file for the Google Drive Service Account):
   - Filename: `credentials/google-credentials.json`
   - Contents: *(paste the raw JSON of your service account key)*
6. Click **Create Web Service**. Wait 3–5 minutes for it to build. Note the generated URL (e.g., `https://metadoc-api.onrender.com`).

---

## Phase 3: Frontend Deployment (Vercel.com)

Vercel provides best-in-class CI/CD for React and Vite projects for free.

1. Go to [Vercel](https://vercel.com/dashboard) and click **Add New → Project**.
2. Import your `MetaDoc-Software-Project-Proposal-Evaluator` GitHub repository.
3. Use the following configuration:
   - **Project Name**: `metadoc-client`
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend/metadoc`
4. Under **Environment Variables**, add the API Base URL property:
   - Name: `VITE_API_BASE_URL`
   - Value: `https://metadoc-api.onrender.com/api/v1` *(replace `metadoc-api.onrender.com` with your ACTUAL Render backend URL from Phase 2)*
5. Click **Deploy**. Vercel will build the frontend within 2 minutes.
6. Once complete, click **Continue to Dashboard** to grab the frontend domain (e.g., `https://metadoc-client.vercel.app`).

---

## Phase 4: Linking and Final Setup

Now that both are online, you need to ensure they can talk to each other properly.

1. **Update Render CORS**:
   - Go back to your Render Dashboard for `metadoc-api`.
   - Update the `CORS_ORIGINS` environment variable to match your exact Vercel Deployment URL (`https://metadoc-client.vercel.app`).
   - *Note: Don't put a trailing slash `/` at the end of the URL!*

2. **Update Google Cloud Console OAuth**:
   - Go to Google Cloud Console → APIs & Services → Credentials.
   - Edit your OAuth 2.0 Client ID.
   - Add your **Vercel domain** (`https://metadoc-client.vercel.app`) to "Authorized JavaScript origins".
   - Add your **Render callback URL** (`https://your-render-url.onrender.com/api/v1/auth/callback`) to "Authorized redirect URIs".
   - Save your changes (these can take 5–10 minutes to propagate).

---

## 💡 Important Notes Regarding Free Tiers

- **Render Cold Starts**: Render's free instances spin down after 15 minutes of inactivity. When a user first opens MetaDoc after a period of idleness, the first API request may take up to 40-50 seconds to complete while the backend wakes up. Once awake, it remains fast. 
- **Vercel Builds**: Fast, automatic, and essentially unlimited for hobby purposes.
- **Supabase Postgres**: Generous limits on reads and writes, amazing dashboard. *(Note: Free tier projects are paused if they receive zero connections for 7 straight days. You can easily unpause them via the Supabase dashboard if this happens).*

Following this guide ensures your architecture lands perfectly within a highly-available, 100% free server ecosystem!
