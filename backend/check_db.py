"""
Check database status and show what needs to be fixed
"""
import sqlite3
import os

db_path = os.path.join('instance', 'metadoc.db')

print("=" * 60)
print("DATABASE STATUS CHECK")
print("=" * 60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check submission_tokens table
cursor.execute("PRAGMA table_info(submission_tokens)")
token_cols = [col[1] for col in cursor.fetchall()]
has_deadline_id = 'deadline_id' in token_cols

print(f"\n✓ submission_tokens.deadline_id exists: {has_deadline_id}")

# Check submissions table  
cursor.execute("PRAGMA table_info(submissions)")
sub_cols = [col[1] for col in cursor.fetchall()]
has_is_late = 'is_late' in sub_cols

print(f"✓ submissions.is_late exists: {has_is_late}")

# Check tokens with deadline_id
if has_deadline_id:
    cursor.execute("SELECT token, deadline_id FROM submission_tokens WHERE deadline_id IS NOT NULL")
    tokens_with_deadline = cursor.fetchall()
    print(f"\n📊 Tokens linked to deadlines: {len(tokens_with_deadline)}")
    for t in tokens_with_deadline[:5]:
        print(f"   - Token: {t[0][:20]}... → Deadline: {t[1][:20]}...")

# Check submissions with deadline_id
cursor.execute("SELECT id, original_filename, deadline_id FROM submissions WHERE deadline_id IS NOT NULL")
subs_with_deadline = cursor.fetchall()
print(f"\n📊 Submissions linked to deadlines: {len(subs_with_deadline)}")
for s in subs_with_deadline[:5]:
    print(f"   - {s[1]} → Deadline: {s[2][:20] if s[2] else 'None'}...")

# Check deadlines
cursor.execute("SELECT id, title FROM deadlines")
deadlines = cursor.fetchall()
print(f"\n📊 Deadlines: {len(deadlines)}")
for d in deadlines:
    cursor.execute("SELECT COUNT(*) FROM submissions WHERE deadline_id = ?", (d[0],))
    count = cursor.fetchone()[0]
    print(f"   - {d[1]}: {count} submissions")

conn.close()

print("\n" + "=" * 60)
if not has_deadline_id:
    print("⚠️  ISSUE: deadline_id column missing in submission_tokens!")
    print("   Run: python add_is_late_column.py")
else:
    print("✅ Database structure is correct!")
    print("\nTo link submissions to deadlines:")
    print("1. Go to Dashboard")
    print("2. Select a deadline from dropdown")
    print("3. Click 'Generate Link'")
    print("4. Use that NEW link to submit files")
    print("5. Submissions will be counted!")
print("=" * 60)
