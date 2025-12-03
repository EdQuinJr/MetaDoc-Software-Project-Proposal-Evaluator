"""
Script to create the metadoc_db database
Run this BEFORE running reset_db.py
"""

import pymysql
import sys

def create_database():
    """Create the metadoc_db database"""
    
    print("=" * 60)
    print("MetaDoc Database Creation Script")
    print("=" * 60)
    print()
    
    # Get database credentials
    print("Enter your MySQL/MariaDB credentials:")
    host = input("Host (default: localhost): ").strip() or "localhost"
    port = input("Port (default: 3306): ").strip() or "3306"
    user = input("Username (default: root): ").strip() or "root"
    password = input("Password: ").strip()
    
    try:
        port = int(port)
    except ValueError:
        print("❌ Invalid port number")
        return
    
    try:
        print("\n🔌 Connecting to MySQL/MariaDB...")
        # Connect without specifying database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE 'metadoc_db'")
        result = cursor.fetchone()
        
        if result:
            print("⚠️  Database 'metadoc_db' already exists!")
            response = input("Do you want to drop and recreate it? (yes/no): ").strip().lower()
            
            if response == 'yes':
                print("\n🗑️  Dropping existing database...")
                cursor.execute("DROP DATABASE metadoc_db")
                print("✓ Database dropped")
            else:
                print("❌ Operation cancelled")
                cursor.close()
                connection.close()
                return
        
        # Create database
        print("\n📦 Creating database 'metadoc_db'...")
        cursor.execute("""
            CREATE DATABASE metadoc_db 
            CHARACTER SET utf8mb4 
            COLLATE utf8mb4_unicode_ci
        """)
        print("✓ Database created successfully!")
        
        # Verify creation
        cursor.execute("SHOW DATABASES LIKE 'metadoc_db'")
        if cursor.fetchone():
            print("\n✅ Database 'metadoc_db' is ready!")
            print("\nNext steps:")
            print("1. Run: python reset_db.py")
            print("2. Run: python run.py")
        else:
            print("❌ Database creation verification failed")
        
        cursor.close()
        connection.close()
        
    except pymysql.err.OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nPlease check:")
        print("- MySQL/MariaDB is running")
        print("- Username and password are correct")
        print("- Host and port are correct")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_database()
