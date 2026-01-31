import sqlite3
from werkzeug.security import generate_password_hash


DATABASE = "task.db"

def get_db_connection():
     conn = sqlite3.connect(DATABASE)
     conn.row_factory = sqlite3.Row
     return conn

def create_tables():

     conn = get_db_connection()
     cursor = conn.cursor()
     print("DEBUG: Inside create_tables() function. About to execute SQL.")
     cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                    last_reminder_sent_at TEXT,
                    reminder_opt_in INTEGER NOT NULL DEFAULT 1
                    )
               ''')
     cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title VARCHAR(100) NOT NULL,
                    description VARCHAR(500),
                    due_date TEXT NOT NULL,
                    status TEXT NOT NULL, 
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
               ''')
     cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tokens(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token VARCHAR(64) UNIQUE NOT NULL,
                    expires_at TEXT NOT NULL,
                    tokenValid INTEGER NOT NULL DEFAULT 1,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
               ''')
     cursor.execute('''
                    CREATE TABLE IF NOT EXISTS activity_log(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    task_id INTEGER,
                    task_title TEXT,
                    timestamp DATATIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
               ''')
     
     conn.commit()
     conn.close()


if __name__ == "__main__":
     create_tables()
     print(f"Database '{DATABASE}' initialized and tables created/checked")

     