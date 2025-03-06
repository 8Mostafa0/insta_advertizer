import sqlite3
import os

db_file = "comments.db"

def connect_db():
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    conn = sqlite3.connect(db_file)
    return conn, conn.cursor()

def count_comments():
    conn, cursor = connect_db()
    cursor.execute("SELECT COUNT(*) FROM comments")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def del_comment(comment_id):
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.close()

def get_comments():
    conn, cursor = connect_db()
    cursor.execute("SELECT text FROM comments")
    result = cursor.fetchall()
    conn.close()
    return result

def get_comment(comment_id):
    conn, cursor = connect_db()
    cursor.execute("SELECT text FROM comments WHERE id = ?", (comment_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_comment(text):
    conn, cursor = connect_db()
    cursor.execute("INSERT INTO comments (text) VALUES (?)", (text,))
    conn.commit()
    conn.close()