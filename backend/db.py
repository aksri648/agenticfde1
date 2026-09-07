import sqlite3
import json

DB_PATH = "conversation.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_message(role: str, content: str, agent: str = None, tool_name: str = None, tool_input: dict = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO messages (role, agent, content, tool_name, tool_input)
        VALUES (?, ?, ?, ?, ?)
    ''', (role, agent, content, tool_name, json.dumps(tool_input) if tool_input else None))
    conn.commit()
    msg_id = c.lastrowid
    conn.close()
    return msg_id

def append_to_last_message(agent: str, content_chunk: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Get last message to see if it's from the same agent
    c.execute('''
        SELECT id, content FROM messages 
        WHERE role = 'agent' AND agent = ? 
        ORDER BY id DESC LIMIT 1
    ''', (agent,))
    row = c.fetchone()
    if row:
        msg_id, current_content = row
        new_content = (current_content or "") + content_chunk
        c.execute('UPDATE messages SET content = ? WHERE id = ?', (new_content, msg_id))
        conn.commit()
    conn.close()

def get_all_messages():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT role, agent, content, tool_name, tool_input FROM messages ORDER BY id ASC')
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

def save_state(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_state(key: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT value FROM state WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
