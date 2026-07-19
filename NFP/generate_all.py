import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

# connection.py
conn_code = """
import sqlite3
from typing import Optional

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn
"""
write_file("src/nfp/infrastructure/database/connection.py", conn_code)

# migrations.py
mig_code = """
import sqlite3

def run_migrations(conn: sqlite3.Connection) -> None:
    pass
"""
write_file("src/nfp/infrastructure/database/migrations.py", mig_code)

# And so on. It's too long.
