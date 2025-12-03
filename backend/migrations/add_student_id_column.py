"""
Migration script to replace student_name and student_email with student_id

Run this script to update the database schema:
python migrations/add_student_id_column.py
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

def migrate():
    app = create_app()
    
    with app.app_context():
        try:
            print("Starting migration: Replace student_name and student_email with student_id")
            
            # Check if student_id column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='submissions' AND column_name='student_id'
            """))
            
            if result.fetchone():
                print("✓ student_id column already exists")
            else:
                # Add student_id column
                print("Adding student_id column...")
                db.session.execute(text("""
                    ALTER TABLE submissions 
                    ADD COLUMN student_id VARCHAR(50)
                """))
                db.session.commit()
                print("✓ Added student_id column")
            
            # Check if old columns exist and drop them
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='submissions' AND column_name='student_name'
            """))
            
            if result.fetchone():
                print("Dropping student_name column...")
                db.session.execute(text("""
                    ALTER TABLE submissions 
                    DROP COLUMN IF EXISTS student_name
                """))
                db.session.commit()
                print("✓ Dropped student_name column")
            else:
                print("✓ student_name column already removed")
            
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='submissions' AND column_name='student_email'
            """))
            
            if result.fetchone():
                print("Dropping student_email column...")
                db.session.execute(text("""
                    ALTER TABLE submissions 
                    DROP COLUMN IF EXISTS student_email
                """))
                db.session.commit()
                print("✓ Dropped student_email column")
            else:
                print("✓ student_email column already removed")
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate()
