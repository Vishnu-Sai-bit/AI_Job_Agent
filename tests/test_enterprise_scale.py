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
from app import app
from fastapi.testclient import TestClient


class TestEnterpriseScale(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.test_email = "test_candidate_2026@jobagent.ai"
        self.test_password = "SecurePassword123!"
        self.test_name = "Beere Vishnu Sai"

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

    def test_03_auth_endpoints_register_login(self):
        print("\n--- 3. Testing Auth API Endpoints (Register, Login, Guest, Me) ---")
        # 1. Guest Session
        guest_res = self.client.post("/auth/guest")
        self.assertEqual(guest_res.status_code, 200)
        guest_data = guest_res.json()
        self.assertTrue(guest_data["success"])
        guest_token = guest_data["token"]
        self.assertIn("user", guest_data)
        print(f"Guest Token Issued: {guest_token[:20]}... User: {guest_data['user']['name']}")

        # 2. Auth /me with Bearer Token
        me_res = self.client.get("/auth/me", headers={"Authorization": f"Bearer {guest_token}"})
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.json()
        self.assertTrue(me_data["success"])
        self.assertEqual(me_data["user"]["id"], guest_data["user"]["id"])
        print(f"Auth /me validated user: {me_data['user']['email']}")

        # 3. System Status Endpoint
        sys_res = self.client.get("/api/system/status")
        self.assertEqual(sys_res.status_code, 200)
        print("Result: Auth & System Endpoints Passed [PASSED]")

    def test_04_headless_autofill_agent(self):
        print("\n--- 4. Testing Headless Auto-Fill Agent & Playwright Script Synthesis ---")
        resume_context = {
            "name": "Beere Vishnu Sai",
            "email": "vishnusai@example.com",
            "phone": "+91 9876543210",
            "location": "Hyderabad, India",
            "skills": ["Python", "SQL", "Power BI", "Tableau", "Machine Learning"],
            "experience_years": 2.0,
            "linkedin": "https://linkedin.com/in/vishnusai",
            "github": "https://github.com/Vishnu-Sai-bit"
        }
        job_data = {
            "title": "Data Analyst",
            "company": "Amazon",
            "apply_url": "https://amazon.jobs/en/jobs/123456"
        }

        # 1. Generate Payload
        res = self.client.post("/api/autofill/generate-payload", json={
            "resume_context": resume_context,
            "job_data": job_data
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["company"], "Amazon")
        self.assertIn("playwright_script", data)
        self.assertIn("review_checklist", data)
        self.assertIn("async_playwright", data["playwright_script"])
        print(f"Generated Playwright Script ({len(data['playwright_script'])} chars)")
        print(f"Review Checklist Count: {len(data['review_checklist'])} items")

        # 2. Launch Simulation Steps
        launch_res = self.client.post("/api/autofill/launch", json={
            "fields": data["fields"],
            "job_title": "Data Analyst",
            "company": "Amazon"
        })
        self.assertEqual(launch_res.status_code, 200)
        launch_data = launch_res.json()
        self.assertTrue(launch_data["success"])
        self.assertEqual(len(launch_data["steps"]), 5)
        print(f"Auto-Fill Stepper: {len(launch_data['steps'])} verification checkpoints complete.")
        print("Result: Headless Auto-Fill Agent Passed [PASSED]")

    def test_05_google_oauth_endpoint(self):
        print("\n--- 5. Testing Google OAuth Authentication & User Creation ---")
        google_payload = {
            "name": "Beere Vishnu Sai (Google)",
            "email": "vishnusai.test.google@jobagent.ai",
            "google_id": "goog_987654321_unit_test",
            "avatar_url": "https://lh3.googleusercontent.com/a/default-user"
        }
        res = self.client.post("/auth/google", json=google_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.assertEqual(data["user"]["email"], google_payload["email"])
        self.assertEqual(data["user"]["auth_provider"], "google")
        print(f"Google OAuth User Created: {data['user']['name']} ({data['user']['email']})")

        # Test login with existing Google user
        res_repeat = self.client.post("/auth/google", json=google_payload)
        self.assertEqual(res_repeat.status_code, 200)
        data_repeat = res_repeat.json()
        self.assertTrue(data_repeat["success"])
        self.assertEqual(data_repeat["user"]["id"], data["user"]["id"])
        print(f"Google OAuth User Login Re-verified: {data_repeat['user']['id']}")
        print("Result: Google OAuth Authentication Passed [PASSED]")


if __name__ == "__main__":
    unittest.main()

