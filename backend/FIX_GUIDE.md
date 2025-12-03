# Fix Guide for Database Errors

## Problem Summary
1. Database `metadoc_db` doesn't exist
2. Database schema needs to be updated (student_name/student_email → student_id)
3. Code references to old schema causing errors

## Solution Steps

### Step 1: Create the Database

Open MySQL/MariaDB command line or phpMyAdmin and run:

```sql
CREATE DATABASE IF NOT EXISTS metadoc_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Or run the SQL file:
```bash
mysql -u root -p < create_database.sql
```

### Step 2: Create Tables with New Schema

Run the reset script to create all tables:

```bash
cd backend
python reset_db.py
```

Type `yes` when prompted. This will create all tables with the correct schema including `student_id`.

### Step 3: Restart Backend Server

```bash
python run.py
```

### Step 4: Test the Application

1. **Login** to the dashboard
2. **Generate a submission token** from the Dashboard
3. **Submit a document** using the token with a student ID (e.g., "22-1686-452")
4. **Check the Files page** to see the submission with student ID

## What Was Fixed

### Backend Changes:
- ✅ `models.py`: Replaced `student_name` and `student_email` with `student_id`
- ✅ `submission.py`: Updated upload and drive link endpoints to use `student_id`
- ✅ `dashboard.py`: Updated all references from `student_name` to `student_id`
- ✅ Migration scripts created for database updates

### Frontend Changes:
- ✅ `SubmitDocument.jsx`: Single "Student ID Number" field instead of name/email
- ✅ `Files.jsx`: Display "Student ID" instead of "Student"
- ✅ Form placeholders show example format: "22-1686-452"

## Troubleshooting

### If you still get "Unknown database" error:
1. Check your database connection in `config.py`
2. Make sure MySQL/MariaDB is running
3. Verify database was created: `SHOW DATABASES;` in MySQL

### If you get "column doesn't exist" errors:
1. Drop and recreate the database:
   ```sql
   DROP DATABASE metadoc_db;
   CREATE DATABASE metadoc_db;
   ```
2. Run `python reset_db.py` again

### If you want to keep existing data:
1. Run the migration script instead:
   ```bash
   python migrations/add_student_id_column.py
   ```
2. Note: Existing submissions will have `student_id` set to NULL

## Database Schema (New)

```sql
submissions table:
- student_id VARCHAR(50)  -- NEW: replaces student_name and student_email
- file_name VARCHAR(255)
- original_filename VARCHAR(255)
- ... (other columns remain the same)
```

## Next Steps

After fixing:
1. Test document submission with student ID
2. Verify Files page displays correctly
3. Check Dashboard overview loads without errors
4. Test deadline creation and management
