"""
Database initialization and migration script for MetaDoc

This script sets up the database schema and handles migrations.
"""

import os
from flask import Flask
from flask_migrate import init, migrate, upgrade
from app import create_app, db
from app.models import *

def init_database():
    """Initialize database with all tables"""
    app = create_app()
    
    with app.app_context():
        print("🗄️  Initializing MetaDoc database...")
        
        # Create all tables
        db.create_all()
        
        # Create initial admin user if none exists
        from app.models import User, UserRole
        
        admin_email = os.environ.get('INITIAL_ADMIN_EMAIL', 'admin@cit.edu')
        
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                name='System Administrator',
                role=UserRole.ADMIN,
                is_active=True
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"✅ Created initial admin user: {admin_email}")
        else:
            print(f"ℹ️  Admin user already exists: {admin_email}")
        
        print("✅ Database initialization complete!")
        
        return True

def create_sample_data():
    """Create sample data for testing (development only)"""
    app = create_app()
    
    if app.config.get('FLASK_ENV') != 'development':
        print("⚠️  Sample data creation is only available in development mode")
        return False
    
    with app.app_context():
        from app.models import User, Deadline, UserRole
        from datetime import datetime, timedelta
        
        print("📊 Creating sample data...")
        
        # Create sample professor
        sample_prof_email = 'prof.sample@cit.edu'
        existing_prof = User.query.filter_by(email=sample_prof_email).first()
        
        if not existing_prof:
            sample_prof = User(
                email=sample_prof_email,
                name='Dr. Sample Professor',
                role=UserRole.PROFESSOR,
                is_active=True
            )
            
            db.session.add(sample_prof)
            db.session.flush()  # Get the ID
            
            # Create sample deadlines
            deadlines = [
                Deadline(
                    title='Research Paper Submission',
                    description='Submit your research paper on software engineering',
                    deadline_datetime=datetime.utcnow() + timedelta(days=14),
                    course_code='SE101',
                    assignment_type='Research Paper',
                    professor_id=sample_prof.id
                ),
                Deadline(
                    title='Project Proposal',
                    description='Submit your capstone project proposal',
                    deadline_datetime=datetime.utcnow() + timedelta(days=7),
                    course_code='CAPSTONE',
                    assignment_type='Project Proposal',
                    professor_id=sample_prof.id
                ),
                Deadline(
                    title='Literature Review',
                    description='Literature review for thesis work',
                    deadline_datetime=datetime.utcnow() - timedelta(days=1),  # Past deadline
                    course_code='THESIS',
                    assignment_type='Literature Review',
                    professor_id=sample_prof.id
                )
            ]
            
            for deadline in deadlines:
                db.session.add(deadline)
            
            db.session.commit()
            
            print(f"✅ Created sample professor: {sample_prof_email}")
            print(f"✅ Created {len(deadlines)} sample deadlines")
        else:
            print(f"ℹ️  Sample professor already exists: {sample_prof_email}")
        
        print("✅ Sample data creation complete!")
        return True

def verify_database():
    """Verify database setup and connectivity"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Verifying database setup...")
            
            # Check database connection
            db.engine.execute('SELECT 1')
            print("✅ Database connection: OK")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = [
                'users', 'submissions', 'analysis_results', 'deadlines',
                'document_snapshots', 'audit_logs', 'report_exports', 'user_sessions'
            ]
            
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            else:
                print(f"✅ All required tables present: {len(expected_tables)} tables")
            
            # Check user count
            from app.models import User
            user_count = User.query.count()
            print(f"ℹ️  Total users: {user_count}")
            
            print("✅ Database verification complete!")
            return True
            
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False

def main():
    """Main function to handle database operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MetaDoc Database Management')
    parser.add_argument('command', choices=['init', 'sample', 'verify'], 
                       help='Database operation to perform')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🗄️  METADOC DATABASE MANAGEMENT")
    print("=" * 60)
    
    if args.command == 'init':
        success = init_database()
    elif args.command == 'sample':
        success = create_sample_data()
    elif args.command == 'verify':
        success = verify_database()
    
    print("=" * 60)
    
    if success:
        print("✅ Operation completed successfully!")
    else:
        print("❌ Operation failed!")
        exit(1)

if __name__ == '__main__':
    main()