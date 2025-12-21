# Backend Utility Scripts

This directory contains utility scripts for managing and maintaining the MetaDoc backend.

## Available Scripts

### `reset_database.py`
Resets the database by deleting the existing database file and creating a fresh one with all tables.

**Usage:**
```bash
# Make sure the backend server is stopped first
python scripts/reset_database.py
```

**What it does:**
- Deletes the existing `metadoc.db` file
- Creates a fresh database with all tables
- Verifies all tables were created successfully

**Important:** Stop the backend server before running this script to avoid file locking issues.

---

## Running Scripts

All scripts should be run from the backend directory:

```bash
cd backend
python scripts/script_name.py
```

## Adding New Scripts

When adding new utility scripts:

1. Place them in the `scripts/` directory
2. Add documentation to this README
3. Include proper error handling
4. Add usage examples
5. Test thoroughly before committing

## Common Use Cases

### Reset Database
When you need to start fresh with a clean database:
```bash
# Stop the backend server (Ctrl+C)
python scripts/reset_database.py
# Restart the backend
python run.py
```

### Future Scripts
Additional utility scripts will be added here as needed for:
- Database migrations
- Data seeding
- Backup and restore
- Performance testing
- Data cleanup
