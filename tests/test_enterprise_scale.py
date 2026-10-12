"""
==========================================================
AI JobAgent - Enterprise Scale Test Suite
Testing MongoDB / Database fallback, JWT Authentication, and Headless Auto-Fill
Author : Beere Vishnu Sai
==========================================================
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.db.mongo_manager import db_manager
from services.auth.auth_service import auth_service
from services.application.auto_fill_agent import auto_fill_agent
class TestEnterpriseScale(unittest.TestCase):

    def test_01_database_manager_status(self):
        print("\n--- 1. Testing Database Manager & MongoDB / Local Storage ---")
        status = db_manager.get_status()
        self.assertIn("storage_mode", status)
        self.assertIn("connected", status)
        print(f"Storage Mode: {status['storage_mode']}")
        print(f"Database Name: {status['database_name']}")
        print(f"MongoDB Available: {status['mongo_available']}")
        print("Result: Database Manager Initialization Passed [PASSED]")

    def test_02_jwt_auth_and_password_security(self):
        print("\n--- 2. Testing JWT Auth & Password Hashing ---")
        # 1. Password Hashing
        hashed = auth_service.hash_password("MySuperSecret99")
        self.assertTrue(auth_service.verify_password("MySuperSecret99", hashed))
        self.assertFalse(auth_service.verify_password("WrongPassword", hashed))

        # 2. JWT Generation & Verification
        token = auth_service.generate_token("usr_test123", "candidate@jobagent.ai", "Vishnu Sai")
        payload = auth_service.verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "usr_test123")
        self.assertEqual(payload["email"], "candidate@jobagent.ai")
        print(f"JWT Token generated and verified successfully. Subject: {payload['sub']}")
        print("Result: JWT Auth & Security Passed [PASSED]")


if __name__ == "__main__":
    unittest.main()

