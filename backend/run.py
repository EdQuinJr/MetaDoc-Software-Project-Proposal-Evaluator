"""
MetaDoc Application Runner

Main entry point for the MetaDoc backend application.
Run this file to start the Flask development server.

Usage:
    python run.py

Environment Variables:
    FLASK_ENV: Set to 'development', 'production', or 'testing'
    DATABASE_URL: Database connection string
    GOOGLE_CLIENT_ID: Google OAuth client ID
    GOOGLE_CLIENT_SECRET: Google OAuth client secret
    And other config variables from .env file
"""

import os
import sys
from app import create_app, db

def main():
    """Main application entry point"""
    
    # Create Flask application
    app = create_app()
    
    # Create database tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created/verified successfully")
        except Exception as e:
            app.logger.error(f"Database setup failed: {e}")
            sys.exit(1)
    
    # Get configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = app.config.get('DEBUG', False)
    
    # Print startup information
    print("\n" + "="*60)
    print("METADOC BACKEND SERVER STARTING")
    print("="*60)
    print(f"Environment: {app.config.get('FLASK_ENV', 'development')}")
    print(f"Debug Mode: {debug}")
    print(f"Server: http://{host}:{port}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')[:50]}...")
    print(f"Google OAuth: {'Configured' if app.config.get('GOOGLE_CLIENT_ID') else 'Not configured'}")
    print(f"Gemini AI: {'Configured' if app.config.get('GEMINI_API_KEY') else 'Not configured'}")
    print("="*60)
    print("\nAPI Endpoints:")
    # ... (endpoints omitted for brevity in replace, but I need to match the block correctly)
    
    # ...
    
    # Since I'm replacing a large block, I'll restrict it to the specific print statements.

    # Actually, I'll use multi_replace to target specific emoji lines.
    print("   Authentication:")
    print("   - POST /api/v1/auth/login")
    print("   - GET  /api/v1/auth/callback")
    print("   - POST /api/v1/auth/validate")
    print("   - POST /api/v1/auth/logout")
    print("\n   File Submission (Module 1):")
    print("   - POST /api/v1/submission/upload")
    print("   - POST /api/v1/submission/drive-link")
    print("   - GET  /api/v1/submission/status/<job_id>")
    print("\n   Metadata Analysis (Module 2):")
    print("   - POST /api/v1/metadata/analyze/<submission_id>")
    print("   - GET  /api/v1/metadata/result/<submission_id>")
    print("\n   Heuristic Insights (Module 3):")
    print("   - POST /api/v1/insights/analyze/<submission_id>")
    print("   - GET  /api/v1/insights/timeliness/<submission_id>")
    print("   - GET  /api/v1/insights/contribution/<submission_id>")
    print("\n   NLP Analysis (Module 4):")
    print("   - POST /api/v1/nlp/analyze/<submission_id>")
    print("   - GET  /api/v1/nlp/readability/<submission_id>")
    print("   - GET  /api/v1/nlp/entities/<submission_id>")
    print("\n   Dashboard (Module 5):")
    print("   - GET  /api/v1/dashboard/overview")
    print("   - GET  /api/v1/dashboard/submissions")
    print("   - GET  /api/v1/dashboard/submissions/<submission_id>")
    print("   - GET  /api/v1/dashboard/deadlines")
    print("   - POST /api/v1/dashboard/deadlines")
    print("\n   Reports:")
    print("   - POST /api/v1/reports/export/pdf")
    print("   - POST /api/v1/reports/export/csv")
    print("   - GET  /api/v1/reports/download/<export_id>")
    print("   - GET  /api/v1/reports/exports")
    print("="*60)
    
    if not app.config.get('GOOGLE_CLIENT_ID'):
        print("\nWARNING: Google OAuth not configured!")
        print("   Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
    
    if not os.path.exists('.env'):
        print("\nWARNING: .env file not found!")
        print("   Copy .env.example to .env and configure your settings")
    
    print("\nReady to serve requests!")
    print("="*60 + "\n")
    
    # Start the development server
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nServer failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()