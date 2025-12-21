"""
Database Reset Script for MetaDoc

This script will:
1. Close all database connections
2. Delete the existing database file
3. Create a fresh database with all tables

Usage:
    python reset_database.py
"""

import os
import sys
import time

# Add parent directory to path so we can import app
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)

# Get the database path (in backend directory, not scripts directory)
DB_PATH = os.path.join(BACKEND_DIR, 'metadoc.db')

print("=" * 60)
print("MetaDoc Database Reset")
print("=" * 60)
print(f"\nDatabase path: {DB_PATH}")

# Check if database exists
if os.path.exists(DB_PATH):
    print(f"Database file found: {os.path.getsize(DB_PATH)} bytes")
    
    # Try to delete the database
    try:
        os.remove(DB_PATH)
        print("[+] Database file deleted successfully")
    except PermissionError:
        print("\n[!] ERROR: Database file is locked by another process")
        print("\nPlease:")
        print("1. Stop the backend server (Ctrl+C in the terminal)")
        print("2. Wait a few seconds")
        print("3. Run this script again")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Error deleting database: {e}")
        sys.exit(1)
else:
    print("No existing database found")

# Wait a moment
time.sleep(1)

# Create fresh database
print("\nCreating fresh database...")

try:
    from app import create_app, db
    
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("[+] Database tables created successfully")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\nCreated {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
    
    print("\n" + "=" * 60)
    print("Database reset complete!")
    print("=" * 60)
    print("\nYou can now start the backend server:")
    print("  python run.py")
    
except Exception as e:
    print(f"\n[X] Error creating database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
