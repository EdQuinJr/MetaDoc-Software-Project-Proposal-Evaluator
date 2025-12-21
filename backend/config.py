import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend directory path
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure database URL
_DB_URL = os.environ.get('DATABASE_URL')
if not _DB_URL:
    # Default to SQLite in backend directory with absolute path
    _db_path = os.path.join(_BACKEND_DIR, 'metadoc.db')
    _DB_URL = f'sqlite:///{_db_path}'

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = _DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or './uploads'
    TEMP_STORAGE_PATH = os.environ.get('TEMP_STORAGE_PATH') or './temp_files'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    
    # Google API Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
    GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE')
    
    # Gemini AI Configuration (Optional)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Institution Configuration
    ALLOWED_EMAIL_DOMAINS = os.environ.get('ALLOWED_EMAIL_DOMAINS', 'cit.edu').split(',')
    INSTITUTION_NAME = os.environ.get('INSTITUTION_NAME') or 'Cebu Institute of Technology - University'
    
    # NLP Configuration
    NLP_MODEL_PATH = os.environ.get('NLP_MODEL_PATH') or './models'
    DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE') or 'en'
    MAX_DOCUMENT_WORDS = int(os.environ.get('MAX_DOCUMENT_WORDS', 15000))
    MIN_DOCUMENT_WORDS = int(os.environ.get('MIN_DOCUMENT_WORDS', 50))
    
    # Report Configuration
    REPORTS_STORAGE_PATH = os.environ.get('REPORTS_STORAGE_PATH') or './reports'
    ENABLE_PDF_EXPORT = os.environ.get('ENABLE_PDF_EXPORT', 'True').lower() == 'true'
    ENABLE_CSV_EXPORT = os.environ.get('ENABLE_CSV_EXPORT', 'True').lower() == 'true'
    
    # Security Configuration
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))
    API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 100))
    ENABLE_AUDIT_LOGGING = os.environ.get('ENABLE_AUDIT_LOGGING', 'True').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or './logs/metadoc.log'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    SQLALCHEMY_ECHO = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}