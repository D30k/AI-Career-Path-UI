import sqlite3

def init_user_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = c.fetchone()

    if not table_exists:
        # Create table with all necessary columns
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                country TEXT,
                age INTEGER,
                gender TEXT,
                highest_education TEXT
            )
        ''')
    else:
        # Get existing columns
        c.execute("PRAGMA table_info(users)")
        existing_columns = [column[1] for column in c.fetchall()]

        # Add any missing columns
        if 'country' not in existing_columns:
            c.execute("ALTER TABLE users ADD COLUMN country TEXT")
        if 'age' not in existing_columns:
            c.execute("ALTER TABLE users ADD COLUMN age INTEGER")
        if 'gender' not in existing_columns:
            c.execute("ALTER TABLE users ADD COLUMN gender TEXT")
        if 'highest_education' not in existing_columns:
            c.execute("ALTER TABLE users ADD COLUMN highest_education TEXT")

    conn.commit()
    conn.close()

init_user_db()
