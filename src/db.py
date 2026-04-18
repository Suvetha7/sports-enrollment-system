from __future__ import annotations

import hashlib
import os
import sqlite3
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "sports_analytics.db"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    ensure_data_dir()
    conn = sqlite3.connect(str(db_path), timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    salt_hex, digest_hex = stored_hash.split(":")
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        120000,
    )
    return digest.hex() == digest_hex


def init_database(db_path: Path | str = DB_PATH) -> None:
    conn = get_connection(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                student_id TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sports_programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                coach_name TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0),
                enrolled_count INTEGER NOT NULL DEFAULT 0 CHECK (enrolled_count >= 0),
                schedule TEXT NOT NULL,
                fee INTEGER NOT NULL DEFAULT 0,
                skill_level TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                program_id INTEGER NOT NULL,
                enrollment_status TEXT NOT NULL DEFAULT 'Confirmed',
                notes TEXT DEFAULT '',
                enrolled_on TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, program_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(program_id) REFERENCES sports_programs(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                actor_email TEXT,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
    finally:
        conn.close()


def database_has_seed_data(db_path: Path | str = DB_PATH) -> bool:
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT COUNT(*) AS count FROM sports_programs").fetchone()
        return bool(row["count"])
    finally:
        conn.close()


def fetch_all(
    query: str,
    params: tuple[Any, ...] = (),
    db_path: Path | str = DB_PATH,
) -> list[dict[str, Any]]:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fetch_one(
    query: str,
    params: tuple[Any, ...] = (),
    db_path: Path | str = DB_PATH,
) -> dict[str, Any] | None:
    conn = get_connection(db_path)
    try:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

