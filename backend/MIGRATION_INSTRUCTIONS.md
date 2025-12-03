# Database Migration Instructions

## Problem
The database schema has been updated to replace `student_name` and `student_email` columns with a single `student_id` column in the `submissions` table.

## Solution Options

### Option 1: Run Migration Script (Preserves Data)
This option will modify the existing database schema while preserving your data.

```bash
cd backend
python migrations/add_student_id_column.py
```

**Note:** Existing submissions will have `student_id` set to NULL since we can't automatically convert names/emails to IDs.

### Option 2: Reset Database (Deletes All Data)
This option will drop all tables and recreate them with the new schema. **All existing data will be lost!**

```bash
cd backend
python reset_db.py
```

When prompted, type `yes` to confirm.

### Option 3: Manual SQL (For PostgreSQL)
If you prefer to run SQL manually:

```sql
-- Add new column
ALTER TABLE submissions ADD COLUMN student_id VARCHAR(50);

-- Drop old columns
ALTER TABLE submissions DROP COLUMN IF EXISTS student_name;
ALTER TABLE submissions DROP COLUMN IF EXISTS student_email;
```

## After Migration

1. Restart your Flask backend server
2. Test by submitting a new document with a student ID (e.g., 22-1686-452)
3. Verify the submission appears correctly in the Files page

## Rollback (If Needed)

If you need to rollback:

```sql
-- Add back old columns
ALTER TABLE submissions ADD COLUMN student_name VARCHAR(255);
ALTER TABLE submissions ADD COLUMN student_email VARCHAR(255);

-- Drop new column
ALTER TABLE submissions DROP COLUMN student_id;
```

Then revert the code changes in:
- `backend/app/models.py`
- `backend/app/modules/submission.py`
- `frontend/metadoc/src/pages/SubmitDocument.jsx`
- `frontend/metadoc/src/pages/Files.jsx`
