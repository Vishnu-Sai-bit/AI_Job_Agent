import unittest
from unittest.mock import patch
from app import create_app

class TestResumeVsPreferences(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_resume_uploaded_without_preferences(self):
        """When resume is uploaded and no preferences entered, matching is driven by resume."""
        mock_ctx = {
            "has_resume": True,
            "has_preferences": False,
            "resume_role": "Python Developer",
            "preferred_role": "",
            "preferred_location": "",
            "skills": ["python", "sql", "fastapi", "docker"],
            "experience_years": 2.0,
            "ats_score": 82.0
        }
        with patch("app.routes.jobs.get_candidate_context", return_value=mock_ctx):
            res = self.client.get("/jobs/")
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            # Verifies that resume matching is active
            self.assertIn("Personalized Resume Matching Active", html)
            self.assertIn("Resume Role: Python Developer", html)
            # Job preferences not set notice is present
            self.assertIn("Preferences: Not set (Using Resume)", html)
            # Search input should not be pre-filled with dummy preference
            self.assertIn('value=""', html)

    def test_preferences_entered_by_user(self):
        """When user explicitly enters and saves job preferences, preferences take effect."""
        mock_ctx = {
            "has_resume": True,
            "has_preferences": True,
            "resume_role": "Python Developer",
            "preferred_role": "Software Engineer",
            "preferred_location": "Bangalore",
            "skills": ["python", "sql", "fastapi", "docker"],
            "experience_years": 2.0,
            "ats_score": 82.0
        }
        with patch("app.routes.jobs.get_candidate_context", return_value=mock_ctx):
            res = self.client.get("/jobs/")
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            # Verifies that Target Preference badge is displayed
            self.assertIn("Target Preference: Software Engineer", html)
            # "Preferences: Not set" should NOT be shown
            self.assertNotIn("Preferences: Not set", html)

if __name__ == "__main__":
    unittest.main()
