import sqlite3

def init_db():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, public_key_n TEXT, public_key_e INTEGER)''')
    # Create messages table with a created_at column for timestamps
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, sender TEXT, recipient TEXT, message TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(sender) REFERENCES users(username),
                  FOREIGN KEY(recipient) REFERENCES users(username))''')
    conn.commit()
    conn.close()

init_db()
