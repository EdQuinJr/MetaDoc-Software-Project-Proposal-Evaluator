import pymysql
import sys

# DB Config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'blank',
    'database': 'metadoc_db',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

print("Checking MySQL Database Schema for 'student_name' column...")

try:
    connection = pymysql.connect(**DB_CONFIG)
    
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'submissions'")
        result = cursor.fetchone()
        
        if not result:
            print("Table 'submissions' does not exist yet. It will be created when you run the app.")
        else:
            # Check columns
            cursor.execute("SHOW COLUMNS FROM submissions LIKE 'student_name'")
            col_result = cursor.fetchone()
            
            if not col_result:
                print("Column 'student_name' missing in 'submissions'. Adding it...")
                cursor.execute("ALTER TABLE submissions ADD COLUMN student_name VARCHAR(255)")
                connection.commit()
                print("✅ Added 'student_name' column successfully.")
            else:
                print("✅ Column 'student_name' already exists.")

    connection.close()
    
except pymysql.MySQLError as e:
    print(f"MySQL Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
