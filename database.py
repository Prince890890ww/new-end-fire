import sqlite3 import os

DB_PATH = "user_data.db"

Ensure DB exists and create tables

def init_db(): conn = sqlite3.connect(DB_PATH) c = conn.cursor()

# User table
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
""")

# User configuration table
c.execute("""
    CREATE TABLE IF NOT EXISTS user_config (
        user_id INTEGER,
        chat_id TEXT,
        name_prefix TEXT,
        delay INTEGER,
        cookies TEXT,
        messages TEXT,
        auto_start INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")

conn.commit()
conn.close()

Run initialization on import

init_db()

Create user

def create_user(username, password): try: conn = sqlite3.connect(DB_PATH) c = conn.cursor() c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password)) conn.commit() conn.close() return True, "Account created successfully!" except sqlite3.IntegrityError: return False, "Username already exists!"

Verify user login

def verify_user(username, password): conn = sqlite3.connect(DB_PATH) c = conn.cursor() c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password)) row = c.fetchone() conn.close() return row[0] if row else None

Get username by ID

def get_username(user_id): conn = sqlite3.connect(DB_PATH) c = conn.cursor() c.execute("SELECT username FROM users WHERE id = ?", (user_id,)) row = c.fetchone() conn.close() return row[0] if row else None

Get user configuration

def get_user_config(user_id): conn = sqlite3.connect(DB_PATH) c = conn.cursor() c.execute("SELECT chat_id, name_prefix, delay, cookies, messages, auto_start FROM user_config WHERE user_id = ?", (user_id,)) row = c.fetchone() conn.close()

if row:
    return {
        'chat_id': row[0],
        'name_prefix': row[1],
        'delay': row[2],
        'cookies': row[3],
        'messages': row[4],
        'auto_start': row[5]
    }
return None

Update user configuration

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages): conn = sqlite3.connect(DB_PATH) c = conn.cursor()

# Check if config exists
c.execute("SELECT 1 FROM user_config WHERE user_id = ?", (user_id,))
exists = c.fetchone()

if exists:
    c.execute("""
        UPDATE user_config 
        SET chat_id=?, name_prefix=?, delay=?, cookies=?, messages=?
        WHERE user_id=?
    """, (chat_id, name_prefix, delay, cookies, messages, user_id))
else:
    c.execute("""
        INSERT INTO user_config (user_id, chat_id, name_prefix, delay, cookies, messages)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, chat_id, name_prefix, delay, cookies, messages))

conn.commit()
conn.close()

Set auto-start

def set_automation_running(user_id, status): conn = sqlite3.connect(DB_PATH) c = conn.cursor() c.execute("UPDATE user_config SET auto_start = ? WHERE user_id = ?", (1 if status else 0, user_id)) conn.commit() conn.close() }

