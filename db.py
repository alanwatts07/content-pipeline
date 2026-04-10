"""SQLite database setup and helpers."""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "pipeline.db"


def get_db() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'paused')),
            target_platforms TEXT DEFAULT '[]',
            target_metrics TEXT DEFAULT '{}',
            created_by TEXT DEFAULT 'operator',
            created_at TEXT DEFAULT (datetime('now')),
            due_date TEXT
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            goal_id TEXT REFERENCES goals(id),
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'done', 'cancelled')),
            task_type TEXT DEFAULT 'write' CHECK(task_type IN ('research', 'write', 'post', 'analyze', 'other')),
            assigned_to TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            completed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS drafts (
            id TEXT PRIMARY KEY,
            task_id TEXT REFERENCES tasks(id),
            goal_id TEXT REFERENCES goals(id),
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            excerpt TEXT DEFAULT '',
            target_platforms TEXT DEFAULT '[]',
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'approved', 'rejected', 'published')),
            created_by TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            approved_at TEXT
        );

        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            draft_id TEXT REFERENCES drafts(id),
            platform TEXT NOT NULL,
            platform_post_id TEXT,
            url TEXT,
            posted_at TEXT DEFAULT (datetime('now')),
            posted_by TEXT
        );

        CREATE TABLE IF NOT EXISTS analytics (
            id TEXT PRIMARY KEY,
            post_id TEXT REFERENCES posts(id),
            platform TEXT NOT NULL,
            checked_at TEXT DEFAULT (datetime('now')),
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            reach INTEGER DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
        CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status);
        CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform);
        CREATE INDEX IF NOT EXISTS idx_posts_draft ON posts(draft_id);
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
