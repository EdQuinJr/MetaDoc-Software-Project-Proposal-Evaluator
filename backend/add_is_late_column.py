"""
Quick script to add missing columns to database tables
Run this script to enable deadline linking and late submission tracking.
"""
import sqlite3
import os

# Path to database
db_path = os.path.join('instance', 'metadoc.db')

print("🔧 MetaDoc Database Migration Script")
print("=" * 50)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Add is_late column to submissions table
    print("\n1️⃣ Checking submissions table...")
    cursor.execute("PRAGMA table_info(submissions)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_late' not in columns:
        print("   Adding is_late column...")
        cursor.execute("ALTER TABLE submissions ADD COLUMN is_late BOOLEAN DEFAULT 0")
        conn.commit()
        print("   ✅ is_late column added!")
    else:
        print("   ✅ is_late column already exists")
    
    # 2. Add deadline_id column to submission_tokens table
    print("\n2️⃣ Checking submission_tokens table...")
    cursor.execute("PRAGMA table_info(submission_tokens)")
    token_columns = [column[1] for column in cursor.fetchall()]
    
    if 'deadline_id' not in token_columns:
        print("   Adding deadline_id column...")
        cursor.execute("ALTER TABLE submission_tokens ADD COLUMN deadline_id TEXT")
        conn.commit()
        print("   ✅ deadline_id column added!")
    else:
        print("   ✅ deadline_id column already exists")
    
    # 3. Verify all tables
    print("\n" + "=" * 50)
    print("📋 VERIFICATION")
    print("=" * 50)
    
    # Verify submissions table
    cursor.execute("PRAGMA table_info(submissions)")
    columns = cursor.fetchall()
    print("\n📁 submissions table:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Verify submission_tokens table
    cursor.execute("PRAGMA table_info(submission_tokens)")
    token_columns = cursor.fetchall()
    print("\n🔑 submission_tokens table:")
    for col in token_columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Show counts
    cursor.execute("SELECT COUNT(*) FROM submissions")
    sub_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM submission_tokens")
    token_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM deadlines")
    deadline_count = cursor.fetchone()[0]
    
    print("\n📊 Current Data:")
    print(f"   - Submissions: {sub_count}")
    print(f"   - Tokens: {token_count}")
    print(f"   - Deadlines: {deadline_count}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n" + "=" * 50)
print("✅ Migration complete!")
print("=" * 50)
print("\n📝 Next steps:")
print("   1. Restart your backend server: python run.py")
print("   2. Create a deadline in the dashboard")
print("   3. Generate a token linked to that deadline")
print("   4. Submit files using that token")
print("   5. Check deadline - submission count will increase!")
print("")
