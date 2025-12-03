"""
Database reset script - Use this to recreate all tables with the updated schema

WARNING: This will delete all existing data!

Run this script:
python reset_db.py
"""

from app import create_app, db
from app.models import (
    User, Submission, AnalysisResult, Deadline, 
    DocumentSnapshot, AuditLog, ReportExport, 
    UserSession, SubmissionToken
)

def reset_database():
    app = create_app()
    
    with app.app_context():
        try:
            print("⚠️  WARNING: This will delete all existing data!")
            response = input("Are you sure you want to continue? (yes/no): ")
            
            if response.lower() != 'yes':
                print("❌ Operation cancelled")
                return
            
            print("\n🗑️  Dropping all tables...")
            db.drop_all()
            print("✓ All tables dropped")
            
            print("\n📦 Creating tables with new schema...")
            db.create_all()
            print("✓ All tables created")
            
            print("\n✅ Database reset completed successfully!")
            print("\nNew schema includes:")
            print("  - student_id (VARCHAR(50)) instead of student_name and student_email")
            print("  - All other tables remain unchanged")
            
        except Exception as e:
            print(f"\n❌ Database reset failed: {e}")
            raise

if __name__ == '__main__':
    reset_database()
