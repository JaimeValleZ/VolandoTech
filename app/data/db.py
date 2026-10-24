import sqlite3
from contextlib import contextmanager

from app.core.config import DATA_DIR

DB_PATH = DATA_DIR / "tutor.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    pages INTEGER NOT NULL,
    char_count INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);
CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    nickname TEXT NOT NULL,
    age INTEGER NOT NULL,
    likes TEXT NOT NULL DEFAULT '',
    easy TEXT NOT NULL DEFAULT '',
    hard TEXT NOT NULL DEFAULT '',
    plan_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS part_cache (
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    band TEXT NOT NULL,
    position INTEGER NOT NULL,
    data_json TEXT NOT NULL,
    PRIMARY KEY (document_id, band, position)
);
CREATE TABLE IF NOT EXISTS readings (
    id TEXT PRIMARY KEY,
    nickname TEXT NOT NULL,
    age INTEGER NOT NULL,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
