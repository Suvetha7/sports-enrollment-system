from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.db import init_database
from src.seed_data import seed_demo_data
from src.services import (
    ValidationError,
    analytics_overview,
    authenticate_user,
    enroll_user_in_program,
    list_programs,
    register_user,
)


class SportsServicesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test.db"
        init_database(self.db_path)
        seed_demo_data(self.db_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_register_user(self) -> None:
        created = register_user(
            {
                "full_name": "Karan Dev",
                "email": "karan.dev@college.edu",
                "student_id": "CSA777",
                "phone": "9000000000",
                "password": "StrongPass1",
            },
            self.db_path,
        )
        self.assertEqual(created["email"], "karan.dev@college.edu")

    def test_duplicate_registration_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            register_user(
                {
                    "full_name": "Another User",
                    "email": "ananya.iyer@college.edu",
                    "student_id": "CSA888",
                    "phone": "9000000001",
                    "password": "StrongPass1",
                },
                self.db_path,
            )

    def test_authenticate_seeded_user(self) -> None:
        user = authenticate_user("ananya.iyer@college.edu", "Sports@123", self.db_path)
        self.assertEqual(user["student_id"], "CSA001")

    def test_enroll_user_in_program(self) -> None:
        programs = list_programs(self.db_path)
        open_program = next(program for program in programs if program["seats_left"] > 0)
        result = enroll_user_in_program("rahul.menon@college.edu", open_program["id"], "", self.db_path)
        self.assertEqual(result["student"], "Rahul Menon")

    def test_duplicate_enrollment_rejected(self) -> None:
        programs = list_programs(self.db_path)
        football_program = next(program for program in programs if program["name"] == "Elite Football Camp")
        with self.assertRaises(ValidationError):
            enroll_user_in_program("ananya.iyer@college.edu", football_program["id"], "", self.db_path)

    def test_analytics_summary(self) -> None:
        overview = analytics_overview(self.db_path)
        self.assertGreaterEqual(overview["summary"]["total_users"], 3)
        self.assertGreaterEqual(overview["summary"]["total_programs"], 6)


if __name__ == "__main__":
    unittest.main()
