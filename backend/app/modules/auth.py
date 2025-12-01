"""
Authentication Module for MetaDoc

Implements SRS requirements:
- M5.UC01: Professor Login via Gmail OAuth
- OAuth 2.0 authentication with Google
- Session management
- Domain-based access control
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, session, redirect, url_for
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
import secrets

from app import db
from app.models import User, UserSession, UserRole
from app.services.audit_service import AuditService

auth_bp = Blueprint('auth', __name__)

class AuthenticationService:
    """Service for handling OAuth authentication and session management"""
    
    def __init__(self):
        self.google_client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        self.google_client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        self.allowed_domains = current_app.config.get('ALLOWED_EMAIL_DOMAINS', [])
    
    def get_google_auth_url(self, user_type='professor'):
        """Generate Google OAuth authorization URL"""
        try:
            # Create OAuth flow
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
            
            # Generate authorization URL with state for CSRF protection
            state = secrets.token_urlsafe(32)
            session['oauth_state'] = state
            session['user_type'] = user_type  # Store user type in session
            
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
            # Verify state parameter for CSRF protection
            if state != session.get('oauth_state'):
                return None, "Invalid OAuth state"
            
            # Create OAuth flow
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
            
            # Exchange authorization code for tokens
            flow.fetch_token(code=authorization_code)
            
            # Get user info from ID token
            credentials = flow.credentials
            # Add clock skew tolerance of 10 seconds
            id_info = id_token.verify_oauth2_token(
                credentials.id_token,
                google_requests.Request(),
                self.google_client_id,
                clock_skew_in_seconds=10
            )
            
            # Extract user information
            google_id = id_info.get('sub')
            email = id_info.get('email')
            name = id_info.get('name')
            picture = id_info.get('picture')
            email_verified = id_info.get('email_verified', False)
            
            if not email_verified:
                return None, "Email not verified with Google"
            
            # Check domain restrictions
            if self.allowed_domains and not self._is_domain_allowed(email):
                AuditService.log_authentication_event('login_attempt', email, False, 'Domain not allowed')
                return None, f"Access restricted to domains: {', '.join(self.allowed_domains)}"
            
            # Create or update user
            user = self._create_or_update_user(
                google_id=google_id,
                email=email,
                name=name,
                picture=picture
            )
            
            if not user:
                return None, "Failed to create user account"
            
            # Create user session
            session_token = self._create_user_session(
                user=user,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                expires_at=credentials.expiry
            )
            
            if not session_token:
                return None, "Failed to create session"
            
            # Log successful authentication
            AuditService.log_authentication_event('login_success', email, True)
            
            return {
                'user': user.to_dict(),
                'session_token': session_token,
                'expires_at': (datetime.utcnow() + timedelta(hours=current_app.config.get('SESSION_TIMEOUT', 3600) // 3600)).isoformat()
            }, None
            
        except Exception as e:
            current_app.logger.error(f"OAuth callback handling failed: {e}")
            if 'email' in locals():
                AuditService.log_authentication_event('login_error', email, False, str(e))
            return None, f"Authentication error: {e}"
    
    def _is_domain_allowed(self, email):
        """Check if email domain is in allowed list"""
        if not self.allowed_domains:
            return True  # No restrictions
        
        email_domain = email.split('@')[1].lower()
        return any(email_domain == domain.lower() or email_domain.endswith(f'.{domain.lower()}') 
                  for domain in self.allowed_domains)
    
    def _create_or_update_user(self, google_id, email, name, picture):
        """Create new user or update existing user"""
        try:
            # Get user type from session
            user_type = session.get('user_type', 'professor')
            role = UserRole.STUDENT if user_type == 'student' else UserRole.PROFESSOR
            
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Update existing user
                user.google_id = google_id
                user.name = name
                user.profile_picture = picture
                user.last_login = datetime.utcnow()
                user.is_active = True
                # Update role based on login type
                user.role = role
            else:
                # Create new user
                user = User(
                    email=email,
                    name=name,
                    google_id=google_id,
                    profile_picture=picture,
                    role=role,
                    last_login=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(user)
            
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"User creation/update failed: {e}")
            return None
    
    def _create_user_session(self, user, access_token, refresh_token, expires_at):
        """Create user session with encrypted tokens"""
        try:
            # Generate session token
            session_token = secrets.token_urlsafe(64)
            
            # Calculate session expiry
            session_expiry = datetime.utcnow() + timedelta(
                seconds=current_app.config.get('SESSION_TIMEOUT', 3600)
            )
            
            # Create session record
            user_session = UserSession(
                session_token=session_token,
                user_id=user.id,
                expires_at=session_expiry,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                user_agent=request.headers.get('User-Agent'),
                google_access_token=self._encrypt_token(access_token) if access_token else None,
                google_refresh_token=self._encrypt_token(refresh_token) if refresh_token else None,
                token_expires_at=expires_at
            )
            
            db.session.add(user_session)
            db.session.commit()
            
            return session_token
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Session creation failed: {e}")
            return None
    
    def _encrypt_token(self, token):
        """Encrypt token for secure storage (simplified implementation)"""
        # In production, use proper encryption library like Fernet
        # This is a placeholder for the encryption logic
        return token  # TODO: Implement proper token encryption
    
    def validate_session(self, session_token):
        """Validate user session token"""
        try:
            if not session_token:
                return None, "No session token provided"
            
            # Find active session
            user_session = UserSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if not user_session:
                return None, "Invalid session token"
            
            # Check expiry
            if user_session.expires_at < datetime.utcnow():
                user_session.is_active = False
                db.session.commit()
                return None, "Session expired"
            
            # Get user
            user = User.query.filter_by(id=user_session.user_id, is_active=True).first()
            
            if not user:
                return None, "User account not found or inactive"
            
            return {
                'user': user,
                'session': user_session
            }, None
            
        except Exception as e:
            current_app.logger.error(f"Session validation failed: {e}")
            return None, "Session validation error"
    
    def logout_user(self, session_token):
        """Logout user and invalidate session"""
        try:
            user_session = UserSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if user_session:
                user_session.is_active = False
                db.session.commit()
                
                # Log logout event
                user = User.query.filter_by(id=user_session.user_id).first()
                if user:
                    AuditService.log_authentication_event('logout', user.email, True)
                
                return True, None
            else:
                return False, "Session not found"
                
        except Exception as e:
            current_app.logger.error(f"Logout failed: {e}")
            return False, f"Logout error: {e}"

# Initialize service lazily to avoid accessing current_app during import
auth_service = None

def get_auth_service():
    """Get or create the authentication service instance"""
    global auth_service
    if auth_service is None:
        auth_service = AuthenticationService()
    return auth_service

@auth_bp.route('/login', methods=['GET'])
def initiate_login():
    """
    Initiate Google OAuth login
    
    SRS Reference: M5.UC01 - Professor Login via Gmail OAuth
    """
    try:
        # Get user type from query parameter (student or professor)
        user_type = request.args.get('user_type', 'professor')
        
        auth_url, error = get_auth_service().get_google_auth_url(user_type)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'auth_url': auth_url,
            'message': 'Redirect to auth_url to complete login'
        })
        
    except Exception as e:
        current_app.logger.error(f"Login initiation failed: {e}")
        return jsonify({'error': 'Authentication service unavailable'}), 500

@auth_bp.route('/callback', methods=['GET'])
def oauth_callback():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code and state from callback
        authorization_code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            return jsonify({'error': f'OAuth error: {error}'}), 400
        
        if not authorization_code:
            return jsonify({'error': 'No authorization code received'}), 400
        
        # Process OAuth callback
        result, error = get_auth_service().handle_oauth_callback(authorization_code, state)
        
        if error:
            # Redirect to frontend with error
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
            return redirect(f"{frontend_url}/auth/callback?error={error}")
        
        # Redirect to frontend with session token and user data
        import urllib.parse
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        user_json = urllib.parse.quote(json.dumps(result['user']))
        return redirect(
            f"{frontend_url}/auth/callback?session_token={result['session_token']}&user={user_json}"
        )
        
    except Exception as e:
        current_app.logger.error(f"OAuth callback failed: {e}")
        return jsonify({'error': 'Authentication failed'}), 500

@auth_bp.route('/validate', methods=['POST'])
def validate_session():
    """Validate user session token"""
    try:
        data = request.get_json()
        session_token = data.get('session_token') if data else None
        
        if not session_token:
            # Try to get from Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                session_token = auth_header[7:]
        
        result, error = get_auth_service().validate_session(session_token)
        
        if error:
            return jsonify({'valid': False, 'error': error}), 401
        
        return jsonify({
            'valid': True,
            'user': result['user'].to_dict(),
            'session_info': {
                'expires_at': result['session']['expires_at'].isoformat(),
                'created_at': result['session']['created_at'].isoformat()
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Session validation failed: {e}")
        return jsonify({'valid': False, 'error': 'Validation error'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user and invalidate session"""
    try:
        data = request.get_json()
        session_token = data.get('session_token') if data else None
        
        if not session_token:
            # Try to get from Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                session_token = auth_header[7:]
        
        if not session_token:
            return jsonify({'error': 'No session token provided'}), 400
        
        success, error = get_auth_service().logout_user(session_token)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'message': 'Logged out successfully',
            'success': success
        })
        
    except Exception as e:
        current_app.logger.error(f"Logout failed: {e}")
        return jsonify({'error': 'Logout error'}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_user_profile():
    """Get current user profile information"""
    try:
        # Get session token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        session_token = auth_header[7:]
        
        # Validate session
        result, error = get_auth_service().validate_session(session_token)
        
        if error:
            return jsonify({'error': error}), 401
        
        user = result['user']
        
        # Get additional user statistics
        from app.models import Submission, Deadline
        
        user_stats = {
            'total_submissions_reviewed': Submission.query.filter_by(professor_id=user.id).count(),
            'active_deadlines': Deadline.query.filter_by(professor_id=user.id).filter(
                Deadline.deadline_datetime > datetime.utcnow()
            ).count(),
            'account_created': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        return jsonify({
            'user': user.to_dict(),
            'statistics': user_stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Profile retrieval failed: {e}")
        return jsonify({'error': 'Profile retrieval error'}), 500

@auth_bp.route('/generate-submission-token', methods=['POST'])
def generate_submission_token():
    """
    Generate a token for student submission portal access
    Only professors can generate tokens
    """
    try:
        # Get session token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        session_token = auth_header[7:]
        
        # Validate session
        result, error = get_auth_service().validate_session(session_token)
        
        if error:
            return jsonify({'error': error}), 401
        
        user = result['user']
        
        # Check if user is professor
        if user.role != UserRole.PROFESSOR:
            return jsonify({'error': 'Only professors can generate submission tokens'}), 403
        
        # Get deadline_id from request body (optional)
        data = request.get_json() or {}
        deadline_id = data.get('deadline_id')
        
        # Validate deadline if provided
        if deadline_id:
            from app.models import Deadline
            deadline = Deadline.query.filter_by(id=deadline_id, professor_id=user.id).first()
            if not deadline:
                return jsonify({'error': 'Invalid deadline or access denied'}), 404
        
        # Generate submission token (valid for 30 days)
        submission_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Store token with deadline link
        from app.models import SubmissionToken
        
        # Try to create token with deadline_id, fallback if column doesn't exist
        try:
            token_record = SubmissionToken(
                token=submission_token,
                professor_id=user.id,
                deadline_id=deadline_id,  # Link to deadline
                expires_at=expires_at,
                is_active=True
            )
            db.session.add(token_record)
            db.session.commit()
        except Exception as e:
            # If deadline_id column doesn't exist, create without it
            current_app.logger.warning(f"Creating token without deadline_id: {e}")
            db.session.rollback()
            token_record = SubmissionToken(
                token=submission_token,
                professor_id=user.id,
                expires_at=expires_at,
                is_active=True
            )
            db.session.add(token_record)
            db.session.commit()
            deadline_id = None  # Reset deadline_id for response
        
        # Get deadline info for response
        deadline_info = None
        if deadline_id:
            deadline = Deadline.query.filter_by(id=deadline_id).first()
            if deadline:
                deadline_info = {
                    'id': deadline.id,
                    'title': deadline.title,
                    'deadline_datetime': deadline.deadline_datetime.isoformat()
                }
        
        return jsonify({
            'token': submission_token,
            'expires_at': expires_at.isoformat(),
            'deadline': deadline_info,
            'submission_url': f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/submit?token={submission_token}"
        })
        
    except Exception as e:
        current_app.logger.error(f"Token generation failed: {e}")
        return jsonify({'error': 'Failed to generate token'}), 500


# Helper functions for password hashing
def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user with email and password
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # Validation
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(
            email=email,
            name=name,
            password_hash=hash_password(password),
            role=UserRole.PROFESSOR,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log registration
        AuditService.log_authentication_event('register', email, True)
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration failed: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login-basic', methods=['POST'])
def login_basic():
    """
    Login with email and password
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            AuditService.log_authentication_event('login_attempt', email, False, 'User not found')
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user has password (might be OAuth-only user)
        if not user.password_hash:
            return jsonify({'error': 'Please use Google Sign-In for this account'}), 401
        
        # Verify password
        if not verify_password(password, user.password_hash):
            AuditService.log_authentication_event('login_attempt', email, False, 'Invalid password')
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        # Create session
        session_token = secrets.token_urlsafe(64)
        session_expiry = datetime.utcnow() + timedelta(
            seconds=current_app.config.get('SESSION_TIMEOUT', 3600)
        )
        
        user_session = UserSession(
            session_token=session_token,
            user_id=user.id,
            expires_at=session_expiry,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent'),
            is_active=True
        )
        
        db.session.add(user_session)
        db.session.commit()
        
        # Log successful login
        AuditService.log_authentication_event('login_success', email, True)
        
        return jsonify({
            'message': 'Login successful',
            'session_token': session_token,
            'user': user.to_dict(),
            'expires_at': session_expiry.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Login failed: {e}")
        return jsonify({'error': 'Login failed'}), 500