import sqlite3
import numpy as np

DB_PATH = 'file_search.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            full_path TEXT UNIQUE,
            parent_path TEXT,
            name TEXT,
            is_folder BOOLEAN,
            size_bytes INTEGER,
            create_time INTEGER,
            is_hidden BOOLEAN,
            is_system BOOLEAN,
            is_temp BOOLEAN,
            vector_blob BLOB
        )
    ''')
    conn.commit()
    conn.close()

def insert_files(batch):
    conn = sqlite3.connect(DB_PATH)
    conn.executemany('''
        INSERT OR REPLACE INTO files 
        (full_path, parent_path, name, is_folder, size_bytes, create_time, is_hidden, is_system, is_temp, vector_blob)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', batch)
    conn.commit()
    conn.close()

def get_all_files():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Limit to 500 nodes for MVP performance
    cursor.execute('SELECT id, name, full_path, vector_blob FROM files LIMIT 500')
    rows = cursor.fetchall()
    conn.close()
    
    files = []
    for row in rows:
        vec = np.frombuffer(row[3], dtype=np.float32)
        files.append({
            'id': row[0],
            'name': row[1],
            'path': row[2],
            'vector': vec
        })
    return files
