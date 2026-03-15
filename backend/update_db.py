import sqlite3
import shutil

shutil.copyfile('metadoc.db', 'metadoc_backup.db')
conn = sqlite3.connect('metadoc.db')

# Create the new table
conn.execute('''
CREATE TABLE new_students (
    id VARCHAR(36) NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    course_year VARCHAR(100),
    team_code VARCHAR(100),
    is_registered BOOLEAN NOT NULL,
    registration_date DATETIME,
    professor_id VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    PRIMARY KEY (id),
    CONSTRAINT _student_professor_uc UNIQUE (student_id, professor_id),
    FOREIGN KEY(professor_id) REFERENCES users (id) ON DELETE CASCADE
)
''')

# Get existing students and find their professor_id via deadlines
students = conn.execute('SELECT id, student_id, last_name, first_name, email, is_registered, registration_date, deadline_id, created_at, updated_at FROM students').fetchall()

for row in students:
    s_id, student_id, last_name, first_name, email, is_reg, reg_date, deadline_id, created_at, updated_at = row
    
    # get prof id
    prof_row = conn.execute('SELECT professor_id FROM deadlines WHERE id=?', (deadline_id,)).fetchone()
    if not prof_row:
        continue # Orphan
    prof_id = prof_row[0]
    
    # insert
    try:
        conn.execute('''
            INSERT INTO new_students (id, student_id, last_name, first_name, email, is_registered, registration_date, professor_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (s_id, student_id, last_name, first_name, email, is_reg, reg_date, prof_id, created_at, updated_at))
    except sqlite3.IntegrityError:
        # ignore duplicates
        pass

conn.execute('DROP TABLE students')
conn.execute('ALTER TABLE new_students RENAME TO students')

conn.commit()
print("Done")
