import sqlite3
import os

def get_db_connection():
    os.makedirs('instance', exist_ok=True)
    conn = sqlite3.connect('instance/database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_quiz_score(user_id, subject, score):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO quiz_scores (user_id, subject, score) VALUES (?, ?, ?)',
        (user_id, subject, score)
    )
    conn.commit()
    conn.close()

def get_user_scores(user_id):
    conn = get_db_connection()
    scores = conn.execute(
        'SELECT subject, score, created_at FROM quiz_scores WHERE user_id = ? ORDER BY created_at DESC LIMIT 10',
        (user_id,)
    ).fetchall()
    conn.close()
    return scores