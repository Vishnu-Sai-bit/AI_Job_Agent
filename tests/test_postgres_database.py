"""
==========================================================
AI JobAgent - PostgreSQL & Database Integration Tests
Author : Beere Vishnu Sai
==========================================================
"""

import unittest
from services.db.postgres_manager import PostgresManager
from services.auth.auth_service import AuthService
from services.db.mongo_manager import db_manager


class TestPostgresDatabase(unittest.TestCase):
    """Test suite for PostgreSQL and multi-database connectivity."""

    def setUp(self):
        self.pg = PostgresManager(db_url="sqlite:///:memory:")

    def test_01_postgres_initialization(self):
        """Test PostgreSQL / SQLAlchemy engine initialization."""
        self.assertTrue(self.pg.is_connected)
        status = self.pg.get_status()
        self.assertIn("connected", status)
        self.assertTrue(status["connected"])

    def test_02_postgres_user_crud(self):
        """Test user creation, retrieval, and updating in SQL/Postgres."""
        user_data = {
            "email": "vishnusai.test.pg@gmail.com",
            "name": "Beere Vishnu Sai (PG)",
            "auth_provider": "google",
            "google_id": "goog_pg_999",
            "role": "candidate",
            "hub": "Hyderabad, India"
        }
        created = self.pg.create_user(user_data)
        self.assertEqual(created["email"], "vishnusai.test.pg@gmail.com")

        fetched = self.pg.get_user_by_email("vishnusai.test.pg@gmail.com")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["name"], "Beere Vishnu Sai (PG)")

        updated = self.pg.update_user(fetched["id"], {"hub": "Bengaluru, India"})
        self.assertIsNotNone(updated)
        self.assertEqual(updated["hub"], "Bengaluru, India")

    def test_03_postgres_application_crm(self):
        """Test application saving and retrieval in SQL/Postgres."""
        app_doc = {
            "user_id": "usr_test_pg",
            "company": "Google",
            "title": "Data Analyst",
            "location": "Bangalore, India",
            "status": "Applied",
            "match_score": 95.0,
            "salary": "₹12-15 LPA"
        }
        saved = self.pg.save_application(app_doc)
        self.assertEqual(saved["company"], "Google")

        apps = self.pg.get_applications(user_id="usr_test_pg")
        self.assertGreaterEqual(len(apps), 1)
        self.assertEqual(apps[0]["company"], "Google")

    def test_04_google_auth_service(self):
        """Test Google OAuth user authentication flow."""
        res = AuthService.authenticate_google_user(
            name="Beere Vishnu Sai (Google Auth)",
            email="vishnusai.google.auth@gmail.com",
            google_id="goog_real_auth_123"
        )
        self.assertTrue(res["success"])
        self.assertIn("token", res)
        self.assertEqual(res["user"]["email"], "vishnusai.google.auth@gmail.com")


if __name__ == "__main__":
    unittest.main()
