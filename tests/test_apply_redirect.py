"""
Test apply_redirect and exact job URL resolution with Job ID
"""
import unittest
from app import create_app
from app.routes.jobs import resolve_exact_job_url

class TestApplyRedirect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_resolve_exact_job_url_for_generic_portal(self):
        job = {
            "id": 1,
            "title": "Data Analyst",
            "company": "Google",
            "location": "Bangalore",
            "url": "https://careers.google.com/jobs/results/?q=Data%20Analyst%20Bangalore"
        }
        resolved = resolve_exact_job_url(job)
        self.assertIn("currentJobId=", resolved)
        self.assertIn("linkedin.com/jobs/search", resolved)
        self.assertIn("Data+Analyst+Google", resolved)
        self.assertTrue(bool(job.get("job_id")))

    def test_resolve_exact_job_url_preserves_live_board_id(self):
        live_job = {
            "id": "live_remotive_1",
            "title": "Tech Lead Full-Stack Rails Engineer",
            "company": "Remotive Tech",
            "url": "https://remotive.com/remote-jobs/software-development/tech-lead-full-stack-rails-engineer-2069746"
        }
        resolved = resolve_exact_job_url(live_job)
        self.assertEqual(resolved, live_job["url"])
        self.assertIn("2069746", resolved)

    def test_apply_redirect_route(self):
        response = self.client.get("/jobs/1/apply", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        location = response.headers.get("Location")
        self.assertIsNotNone(location)
        self.assertIn("careers.google.com", location)
        self.assertIn("4464214853", location)

if __name__ == "__main__":
    unittest.main()
