import sqlite3
import config
from datetime import datetime

def get_conn():
    return sqlite3.connect(config.DB_FILE)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Предложки
    c.execute('''
        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id TEXT,
            file_path TEXT,
            status TEXT DEFAULT 'pending',
            message_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Посты (для статистики и бэкапа)
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_chat_id INTEGER,
            source_message_id INTEGER,
            target_message_id INTEGER,
            post_type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Статистика просмотров (если доступно)
    c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            views INTEGER DEFAULT 0,
            forwards INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Роли пользователей
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            role TEXT DEFAULT 'user',  -- user, moderator, admin
            username TEXT,
            first_name TEXT
        )
    ''')

    # Бэкапы
    c.execute('''
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_chat_id INTEGER,
            backup_chat_id INTEGER,
            last_message_id INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active'
        )
    ''')

    conn.commit()
    conn.close()

# === ПРЕДЛОЖКИ ===
def add_proposal(user_id, file_id, file_path, message_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO proposals (user_id, file_id, file_path, message_id) VALUES (?, ?, ?, ?)',
              (user_id, file_id, file_path, message_id))
    conn.commit()
    proposal_id = c.lastrowid
    conn.close()
    return proposal_id

def get_pending_proposals():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, file_path, user_id, message_id FROM proposals WHERE status = "pending" ORDER BY timestamp')
    rows = c.fetchall()
    conn.close()
    return rows

def update_proposal_status(proposal_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE proposals SET status = ? WHERE id = ?', (status, proposal_id))
    conn.commit()
    conn.close()

# === ПОСТЫ ===
def log_post(source_chat_id, source_message_id, target_message_id, post_type='photo'):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO posts (source_chat_id, source_message_id, target_message_id, post_type) VALUES (?, ?, ?, ?)',
              (source_chat_id, source_message_id, target_message_id, post_type))
    conn.commit()
    conn.close()

# === РОЛИ ===
def get_user_role(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 'user'

def set_user_role(user_id, role, username=None, first_name=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (user_id, role, username, first_name) VALUES (?, ?, ?, ?)',
              (user_id, role, username, first_name))
    conn.commit()
    conn.close()

# === БЭКАПЫ ===
def create_backup_record(source_chat_id, backup_chat_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO backups (source_chat_id, backup_chat_id) VALUES (?, ?)',
              (source_chat_id, backup_chat_id))
    conn.commit()
    backup_id = c.lastrowid
    conn.close()
    return backup_id

def get_active_backups():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT source_chat_id, backup_chat_id, last_message_id FROM backups WHERE status = "active"')
    rows = c.fetchall()
    conn.close()
    return rows

def update_backup_last_id(backup_id, last_message_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE backups SET last_message_id = ? WHERE id = ?', (last_message_id, backup_id))
    conn.commit()
    conn.close()