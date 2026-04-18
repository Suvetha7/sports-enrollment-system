from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from src.db import DB_PATH, get_connection, hash_password, verify_password

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(ValueError):
    pass


def _clean_text(value: str, field_name: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValidationError(f"{field_name} is required.")
    return cleaned


def register_user(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> dict[str, Any]:
    full_name = _clean_text(payload.get("full_name", ""), "Full name")
    email = _clean_text(payload.get("email", ""), "Email").lower()
    student_id = _clean_text(payload.get("student_id", ""), "Student ID").upper()
    phone = _clean_text(payload.get("phone", ""), "Phone")
    password = _clean_text(payload.get("password", ""), "Password")

    if not EMAIL_RE.match(email):
        raise ValidationError("Enter a valid email address.")
    if len(password) < 8:
        raise ValidationError("Password must contain at least 8 characters.")
    if len(student_id) < 5:
        raise ValidationError("Student ID looks too short.")

    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT INTO users (full_name, email, student_id, phone, password_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email, student_id, phone, hash_password(password)),
        )
        conn.execute(
            """
            INSERT INTO audit_log (action_type, actor_email, details)
            VALUES ('USER_REGISTERED', ?, ?)
            """,
            (email, f"Student {full_name} created a portal account"),
        )
        row = conn.execute(
            "SELECT id, full_name, email, student_id, phone, created_at FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        return dict(row)
    except sqlite3.IntegrityError as exc:
        message = str(exc).lower()
        if "users.email" in message:
            raise ValidationError("This email is already registered.") from exc
        if "users.student_id" in message:
            raise ValidationError("This student ID already exists.") from exc
        raise ValidationError("Unable to register user because of duplicate data.") from exc
    finally:
        conn.close()


def authenticate_user(email: str, password: str, db_path: Path | str = DB_PATH) -> dict[str, Any]:
    normalized_email = _clean_text(email, "Email").lower()
    password = _clean_text(password, "Password")
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT id, full_name, email, student_id, phone, password_hash
            FROM users
            WHERE email = ?
            """,
            (normalized_email,),
        ).fetchone()
        if not row or not verify_password(password, row["password_hash"]):
            raise ValidationError("Invalid email or password.")
        conn.execute(
            """
            INSERT INTO audit_log (action_type, actor_email, details)
            VALUES ('USER_LOGIN', ?, 'Student logged into the sports portal')
            """,
            (normalized_email,),
        )
        return {
            "id": row["id"],
            "full_name": row["full_name"],
            "email": row["email"],
            "student_id": row["student_id"],
            "phone": row["phone"],
        }
    finally:
        conn.close()


def enroll_user_in_program(
    email: str,
    program_id: int,
    notes: str = "",
    db_path: Path | str = DB_PATH,
) -> dict[str, Any]:
    normalized_email = _clean_text(email, "Email").lower()
    conn = get_connection(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        user = conn.execute(
            "SELECT id, full_name, email FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()
        if not user:
            raise ValidationError("Register before attempting enrollment.")

        program = conn.execute(
            """
            SELECT id, name, capacity, enrolled_count, status
            FROM sports_programs
            WHERE id = ?
            """,
            (program_id,),
        ).fetchone()
        if not program:
            raise ValidationError("Selected sports program was not found.")
        if program["status"] != "Open":
            raise ValidationError("This program is not open for enrollment.")
        if program["enrolled_count"] >= program["capacity"]:
            raise ValidationError("No seats available in this program.")

        duplicate = conn.execute(
            """
            SELECT 1
            FROM enrollments
            WHERE user_id = ? AND program_id = ?
            """,
            (user["id"], program_id),
        ).fetchone()
        if duplicate:
            raise ValidationError("This student is already enrolled in the selected program.")

        conn.execute(
            """
            INSERT INTO enrollments (user_id, program_id, enrollment_status, notes)
            VALUES (?, ?, 'Confirmed', ?)
            """,
            (user["id"], program_id, notes.strip()),
        )
        conn.execute(
            """
            UPDATE sports_programs
            SET enrolled_count = enrolled_count + 1
            WHERE id = ?
            """,
            (program_id,),
        )
        conn.execute(
            """
            INSERT INTO audit_log (action_type, actor_email, details)
            VALUES ('ENROLLMENT_CREATED', ?, ?)
            """,
            (normalized_email, f"Enrolled in {program['name']}"),
        )
        updated_program = conn.execute(
            """
            SELECT id, name, capacity, enrolled_count, (capacity - enrolled_count) AS seats_left
            FROM sports_programs
            WHERE id = ?
            """,
            (program_id,),
        ).fetchone()
        conn.commit()
        return {
            "student": user["full_name"],
            "program": updated_program["name"],
            "seats_left": updated_program["seats_left"],
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_programs(db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
                id,
                name,
                category,
                coach_name,
                capacity,
                enrolled_count,
                (capacity - enrolled_count) AS seats_left,
                schedule,
                fee,
                skill_level,
                status
            FROM sports_programs
            ORDER BY category, name
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def recent_enrollments(db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
                e.id,
                u.full_name,
                u.email,
                s.name AS program_name,
                s.category,
                e.enrollment_status,
                e.enrolled_on
            FROM enrollments e
            JOIN users u ON u.id = e.user_id
            JOIN sports_programs s ON s.id = e.program_id
            ORDER BY e.enrolled_on DESC, e.id DESC
            LIMIT 8
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def analytics_overview(db_path: Path | str = DB_PATH) -> dict[str, Any]:
    conn = get_connection(db_path)
    try:
        summary = conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM users) AS total_users,
                (SELECT COUNT(*) FROM sports_programs) AS total_programs,
                (SELECT COUNT(*) FROM enrollments) AS total_enrollments,
                (SELECT COALESCE(SUM(capacity), 0) FROM sports_programs) AS total_capacity,
                (SELECT COALESCE(SUM(enrolled_count), 0) FROM sports_programs) AS total_filled
            """
        ).fetchone()

        by_category = conn.execute(
            """
            SELECT
                category,
                COUNT(*) AS program_count,
                SUM(capacity) AS category_capacity,
                SUM(enrolled_count) AS category_enrollment
            FROM sports_programs
            GROUP BY category
            ORDER BY category_enrollment DESC, category
            """
        ).fetchall()

        top_programs = conn.execute(
            """
            SELECT
                name,
                category,
                capacity,
                enrolled_count,
                ROUND((enrolled_count * 100.0) / capacity, 1) AS occupancy_rate
            FROM sports_programs
            ORDER BY occupancy_rate DESC, enrolled_count DESC
            LIMIT 5
            """
        ).fetchall()

        total_capacity = summary["total_capacity"] or 0
        total_filled = summary["total_filled"] or 0
        occupancy_rate = round((total_filled * 100.0 / total_capacity), 1) if total_capacity else 0.0

        return {
            "summary": {
                "total_users": summary["total_users"],
                "total_programs": summary["total_programs"],
                "total_enrollments": summary["total_enrollments"],
                "total_capacity": total_capacity,
                "total_filled": total_filled,
                "occupancy_rate": occupancy_rate,
            },
            "by_category": [dict(row) for row in by_category],
            "top_programs": [dict(row) for row in top_programs],
        }
    finally:
        conn.close()


def dashboard_payload(db_path: Path | str = DB_PATH) -> dict[str, Any]:
    return {
        "overview": analytics_overview(db_path),
        "programs": list_programs(db_path),
        "recent_enrollments": recent_enrollments(db_path),
    }

