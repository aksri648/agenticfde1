import sqlite3
import json
import uuid
import datetime

DB_PATH = "conversation.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Try to add session_id to existing messages if they exist, or just recreate.
    # To keep it simple, we'll recreate tables for new schema if needed. 
    # Let's just create tables cleanly (assuming we can clear the old db).
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            agent TEXT,
            content TEXT,
            tool_name TEXT,
            tool_input TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS state (
            session_id TEXT,
            key TEXT,
            value TEXT,
            PRIMARY KEY (session_id, key)
        )
    ''')
    conn.commit()
    conn.close()

def create_session(title="New Chat"):
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO sessions (id, title) VALUES (?, ?)', (session_id, title))
    conn.commit()
    conn.close()
    return session_id

def list_sessions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC')
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "updated_at": r[2]} for r in rows]

def update_session_title(session_id: str, title: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (title, session_id))
    conn.commit()
    conn.close()

def save_message(session_id: str, role: str, content: str, agent: str = None, tool_name: str = None, tool_input: dict = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO messages (session_id, role, agent, content, tool_name, tool_input)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, role, agent, content, tool_name, json.dumps(tool_input) if tool_input else None))
    c.execute('UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (session_id,))
    conn.commit()
    msg_id = c.lastrowid
    conn.close()
    return msg_id

def append_to_last_message(session_id: str, agent: str, content_chunk: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, content FROM messages 
        WHERE session_id = ? AND role = 'agent' AND agent = ? 
        ORDER BY id DESC LIMIT 1
    ''', (session_id, agent))
    row = c.fetchone()
    if row:
        msg_id, current_content = row
        new_content = (current_content or "") + content_chunk
        c.execute('UPDATE messages SET content = ? WHERE id = ?', (new_content, msg_id))
        c.execute('UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (session_id,))
        conn.commit()
    conn.close()

def get_all_messages(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT role, agent, content, tool_name, tool_input FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
    rows = c.fetchall()
    conn.close()
    
    msgs = []
    for row in rows:
        msgs.append({
            "role": row[0],
            "agent": row[1],
            "content": row[2] or "",
            "toolName": row[3],
            "toolInput": json.loads(row[4]) if row[4] else None
        })
    return msgs

def save_state(session_id: str, key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO state (session_id, key, value) VALUES (?, ?, ?)', (session_id, key, value))
    conn.commit()
    conn.close()

def get_state(session_id: str, key: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT value FROM state WHERE session_id = ? AND key = ?', (session_id, key))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
