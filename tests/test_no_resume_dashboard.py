"""
Test Dashboard & Job Matches when no resume is uploaded.
Verifies:
1. When no resume is uploaded, dashboard displays '--' for Job Matches, ATS score, etc.
2. When no resume is uploaded, dashboard displays 'No Resume Uploaded Yet' CTA.
3. When no resume is uploaded, jobs page indicates Discovery Mode with Discovery badges.
"""

import unittest
from pathlib import Path
from app import create_app

class TestNoResumeDashboard(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_dashboard_no_resume_matches(self):
        """Dashboard must show '--' for Job Matches and not display 50 job matches."""
        # Ensure default parsed resume does not exist
        cache_path = Path("data/default_parsed_resume.json")
        if cache_path.exists():
            cache_path.unlink()

        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # Job Matches stat card must render '--' when candidate has no resume
        self.assertIn("Job Matches</span>", html)
        self.assertIn("--", html)
        # It must NOT show "50" under Job Matches
        self.assertNotIn('<h3 class="fw-bold text-primary mb-0 mt-1">50</h3>', html)

        # Recent Job Matches must show the empty state CTA
        self.assertIn("No Resume Uploaded Yet", html)
        self.assertIn("Upload Resume to Match Jobs", html)

    def test_jobs_page_discovery_mode_when_no_resume(self):
        """Jobs page should be in Discovery Mode when no resume is uploaded."""
        res = self.client.get("/jobs/")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn("Discovery Mode", html)
        self.assertIn("Discovery", html)

if __name__ == "__main__":
    unittest.main()
