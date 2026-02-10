import sqlite3

DB_NAME = "contratos.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def fetch_all(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def execute(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()
