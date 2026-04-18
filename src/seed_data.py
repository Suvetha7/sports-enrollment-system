from __future__ import annotations

from pathlib import Path

from src.db import DB_PATH, get_connection, hash_password


PROGRAMS = [
    ("Elite Football Camp", "Football", "Coach Arjun Rao", 30, "Mon/Wed/Fri - 6:00 PM", 2500, "Intermediate"),
    ("ShuttlePro Badminton", "Badminton", "Coach Nisha Thomas", 24, "Tue/Thu - 5:00 PM", 2200, "Beginner"),
    ("AquaSprint Swimming", "Swimming", "Coach Vivek Shah", 18, "Daily - 7:00 AM", 3000, "All Levels"),
    ("PowerPlay Basketball", "Basketball", "Coach Kevin D'Souza", 20, "Mon/Thu - 4:30 PM", 2400, "Intermediate"),
    ("Ace Tennis Academy", "Tennis", "Coach Meera Kulkarni", 16, "Sat/Sun - 8:00 AM", 2800, "Advanced"),
    ("TrackMax Athletics", "Athletics", "Coach Ritu Narang", 28, "Daily - 6:30 AM", 2100, "All Levels"),
]

USERS = [
    ("Ananya Iyer", "ananya.iyer@college.edu", "CSA001", "9876543210", "Sports@123"),
    ("Rahul Menon", "rahul.menon@college.edu", "CSA002", "9876501234", "Sports@123"),
    ("Priya S", "priya.s@college.edu", "CSA003", "9876509999", "Sports@123"),
]

ENROLLMENTS = [
    ("ananya.iyer@college.edu", "Elite Football Camp", "Prefers evening batches"),
    ("rahul.menon@college.edu", "AquaSprint Swimming", "Competitive training interest"),
    ("priya.s@college.edu", "ShuttlePro Badminton", "Needs beginner support"),
    ("ananya.iyer@college.edu", "TrackMax Athletics", "Preparing for intramurals"),
]


def seed_demo_data(db_path: Path | str = DB_PATH) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")

        for full_name, email, student_id, phone, password in USERS:
            conn.execute(
                """
                INSERT OR IGNORE INTO users (full_name, email, student_id, phone, password_hash)
                VALUES (?, ?, ?, ?, ?)
                """,
                (full_name, email, student_id, phone, hash_password(password)),
            )

        for name, category, coach_name, capacity, schedule, fee, skill_level in PROGRAMS:
            conn.execute(
                """
                INSERT OR IGNORE INTO sports_programs
                (name, category, coach_name, capacity, enrolled_count, schedule, fee, skill_level, status)
                VALUES (?, ?, ?, ?, 0, ?, ?, ?, 'Open')
                """,
                (name, category, coach_name, capacity, schedule, fee, skill_level),
            )

        for email, program_name, notes in ENROLLMENTS:
            user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            program = conn.execute(
                "SELECT id FROM sports_programs WHERE name = ?",
                (program_name,),
            ).fetchone()
            exists = conn.execute(
                "SELECT 1 FROM enrollments WHERE user_id = ? AND program_id = ?",
                (user["id"], program["id"]),
            ).fetchone()
            if exists:
                continue
            conn.execute(
                """
                INSERT INTO enrollments (user_id, program_id, enrollment_status, notes)
                VALUES (?, ?, 'Confirmed', ?)
                """,
                (user["id"], program["id"], notes),
            )
            conn.execute(
                """
                UPDATE sports_programs
                SET enrolled_count = enrolled_count + 1
                WHERE id = ?
                """,
                (program["id"],),
            )

        conn.execute(
            """
            INSERT INTO audit_log (action_type, actor_email, details)
            VALUES
            ('SYSTEM_INIT', 'system@local', 'Demo data seeded for sports enrollment system'),
            ('ANALYTICS_READY', 'system@local', 'Operational metrics available for dashboard')
            """
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

