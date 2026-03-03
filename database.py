import sqlite3
from datetime import date

DB_NAME = "meds.db"

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    with connect() as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            time TEXT,
            taken_today INTEGER DEFAULT 0,
            last_notified TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            message TEXT
        )
        """)

        defaults = {
            "caregiver_email": "",
            "notify_delay": "15",
            "email_enabled": "0",
            "last_reset_date": str(date.today())
        }

        for k, v in defaults.items():
            c.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)",
                (k, v)
            )

def get_setting(key):
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = c.fetchone()
        return row[0] if row else None

def set_setting(key, value):
    with connect() as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE settings SET value=? WHERE key=?",
            (value, key)
        )

def log(message):
    from datetime import datetime
    with connect() as conn:
        conn.execute(
            "INSERT INTO logs (time, message) VALUES (?,?)",
            (datetime.now().isoformat(timespec="seconds"), message)
        )