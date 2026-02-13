"""
Authentication Service - Handles OAuth authentication and session management

Extracted from api/auth.py to follow proper service layer architecture.
"""

import secrets
import os

# Force insecure transport for local development (must be set before oauth imports)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from datetime import datetime, timedelta
from flask import current_app, session
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.extensions import db
from app.models import User, UserSession, UserRole


class AuthService:
    """Service for handling OAuth authentication and session management"""
    
    def __init__(self):
        pass
    
    @property
    def google_client_id(self):
        return current_app.config.get('GOOGLE_CLIENT_ID')
    
    @property
    def google_client_secret(self):
        return current_app.config.get('GOOGLE_CLIENT_SECRET')
    
    @property
    def redirect_uri(self):
        return current_app.config.get('GOOGLE_REDIRECT_URI')
    
    @property
    def allowed_domains(self):
        return current_app.config.get('ALLOWED_EMAIL_DOMAINS', [])
    
    def get_google_auth_url(self, user_type='professor'):
        """Generate Google OAuth authorization URL"""
        try:
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.google_client_id,
                        "client_secret": self.google_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=[
                    'openid',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'https://www.googleapis.com/auth/drive.readonly'
                ]
            )
            
            flow.redirect_uri = self.redirect_uri
            
            state = secrets.token_urlsafe(32)
            session['oauth_state'] = state
            session['user_type'] = user_type
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state,
                prompt='consent'
            )
            
            return authorization_url, None
            
        except Exception as e:
            current_app.logger.error(f"OAuth URL generation failed: {e}")
            return None, f"Authentication setup error: {e}"
    
    def handle_oauth_callback(self, authorization_code, state):
        """Handle OAuth callback and create user session"""
        try:
            if state != session.get('oauth_state'):
                return None, "Invalid OAuth state"
            
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.google_client_id,
                        "client_secret": self.google_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=[
                    'openid',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'https://www.googleapis.com/auth/drive.readonly'
                ]
            )
            
            flow.redirect_uri = self.redirect_uri
            flow.fetch_token(code=authorization_code)
            
            credentials = flow.credentials
            
            # Store credentials in session for Drive API calls
            session['google_credentials'] = credentials.to_json()
            
            user_info = id_token.verify_oauth2_token(
                credentials.id_token,
                google_requests.Request(),
                self.google_client_id,
                clock_skew_in_seconds=60
            )
            
            email = user_info.get('email')
            name = user_info.get('name')
            picture = user_info.get('picture')
            google_id = user_info.get('sub')
            
            # Domain validation logic
            if self.allowed_domains and self.allowed_domains != ['']:
                domain = email.split('@')[1] if '@' in email else ''
                # Always allow gmail.com and the specific allowed domains
                allowed = [d.strip().lower() for d in self.allowed_domains if d.strip()]
                allowed.append('gmail.com')
                
                if domain not in allowed:
                    return None, f"Email domain '{domain}' not allowed. Allowed domains: {', '.join(allowed)}"
            
            user_type = session.get('user_type', 'professor')
            role = UserRole.PROFESSOR if user_type == 'professor' else UserRole.STUDENT
            
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    email=email,
                    name=name,
                    google_id=google_id,
                    profile_picture=picture,
                    role=role,
                    is_active=True
                )
                db.session.add(user)
            else:
                user.name = name
                user.google_id = google_id
                user.profile_picture = picture
                user.last_login = datetime.utcnow()
            
            db.session.commit()
            
            session_token = secrets.token_urlsafe(32)
            user_session = UserSession(
                user_id=user.id,
                session_token=session_token,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(user_session)
            db.session.commit()
            
            return {
                'user': user,
                'session_token': session_token,
                'expires_at': user_session.expires_at
            }, None
            
        except Exception as e:
            current_app.logger.error(f"OAuth callback failed: {e}")
            return None, f"Authentication failed: {e}"
    
    def validate_session(self, session_token):
        """Validate session token and return user"""
        if not session_token:
            return None, "No session token provided"
        
        user_session = UserSession.query.filter_by(session_token=session_token).first()
        
        if not user_session:
            return None, "Invalid session token"
        
        if user_session.expires_at < datetime.utcnow():
            return None, "Session expired"
        
        user = User.query.filter_by(id=user_session.user_id).first()
        
        if not user or not user.is_active:
            return None, "User not found or inactive"
        
        return {'user': user, 'session': user_session}, None
    
    def logout(self, session_token):
        """Logout user by invalidating session"""
        try:
            user_session = UserSession.query.filter_by(session_token=session_token).first()
            if user_session:
                db.session.delete(user_session)
                db.session.commit()
            return True, None
        except Exception as e:
            current_app.logger.error(f"Logout failed: {e}")
            return False, str(e)
    
    def create_basic_auth_user(self, email, password, name):
        """Create user with basic authentication (for testing)"""
        try:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return None, "User already exists"
            
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            user = User(
                email=email,
                name=name,
                password_hash=password_hash,
                role=UserRole.PROFESSOR,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"User creation failed: {e}")
            return None, str(e)
    
    def validate_basic_auth(self, email, password):
        """Validate basic authentication credentials"""
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.password_hash:
                return None, "Invalid credentials"
            
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash != user.password_hash:
                return None, "Invalid credentials"
            
            if not user.is_active:
                return None, "User account is inactive"
            
            session_token = secrets.token_urlsafe(32)
            user_session = UserSession(
                user_id=user.id,
                session_token=session_token,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(user_session)
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            return {
                'user': user,
                'session_token': session_token,
                'expires_at': user_session.expires_at
            }, None
            
        except Exception as e:
            current_app.logger.error(f"Basic auth validation failed: {e}")
            return None, str(e)
