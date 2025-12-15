import pymysql
import sys

try:
    # Try connecting without selecting a database
    # Assuming 'blank' is the password as per the .env file
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='blank',  
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            # Create the database
            cursor.execute("CREATE DATABASE IF NOT EXISTS metadoc_db")
            print("Successfully created database 'metadoc_db' (or it already existed).")
            
            # Use the database
            cursor.execute("USE metadoc_db")
            print("Successfully selected database 'metadoc_db'.")
            
    finally:
        connection.close()

except pymysql.MySQLError as e:
    print(f"Error accessing MySQL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
