import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    tier TEXT NOT NULL,
    base_premium REAL NOT NULL,
    deductible REAL NOT NULL,
    coverage_limit REAL NOT NULL,
    description TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    age INTEGER NOT NULL,
    plan_id INTEGER NOT NULL REFERENCES plans(id)
);
CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

SEED_PLANS = [
    ("Essential", "bronze", 180.0, 5000.0, 100000.0,
     "Low monthly cost. Covers hospital stays and emergency care."),
    ("Balanced", "silver", 320.0, 2500.0, 250000.0,
     "Adds outpatient visits, prescriptions and maternity cover."),
    ("Complete", "gold", 510.0, 500.0, 600000.0,
     "Low deductible with dental, vision and specialist cover."),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    if conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO plans (name, tier, base_premium, deductible, coverage_limit, description)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            SEED_PLANS,
        )
    conn.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
