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
        self.assertIn("careers.google.com", resolved)
        self.assertIn("Data+Analyst", resolved)
        self.assertNotIn("linkedin.com", resolved)
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
        self.assertTrue("google.com" in location and "careers" in location)
        self.assertIn("Data+Analyst", location)

    def test_apply_redirect_exl_direct_oracle_hcm(self):
        response = self.client.get("/jobs/121/apply", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        location = response.headers.get("Location")
        self.assertIn("oraclecloud.com", location)
        self.assertIn("/sites/CX_2/job/16080", location)
        self.assertNotIn("linkedin.com", location)

    def test_unwrap_destination_apply_link_for_exl(self):
        from services.job_links.link_unwrapper import unwrap_destination_apply_link
        job = {
            "id": "live_linkedin_exl_test",
            "company": "EXL",
            "title": "Senior Data Analyst",
            "url": "https://in.linkedin.com/jobs/view/senior-data-analyst-at-exl-4446724293"
        }
        resolved = unwrap_destination_apply_link(job)
        self.assertIn("oraclecloud.com", resolved)
        self.assertIn("16080", resolved)
        self.assertNotIn("linkedin.com", resolved)

    def test_unwrap_destination_apply_link_for_accenture(self):
        from services.job_links.link_unwrapper import unwrap_destination_apply_link
        job = {
            "id": "live_linkedin_accenture_test",
            "company": "Accenture",
            "title": "Packaged/SaaS Application Engineer",
            "job_id": "ATCI-5816189-S2072200_en",
            "url": "https://in.linkedin.com/jobs/view/packaged-saas-application-engineer-4412345678"
        }
        resolved = unwrap_destination_apply_link(job)
        self.assertIn("accenture.com", resolved)
        self.assertIn("ATCI-5816189-S2072200_en", resolved)
        self.assertNotIn("linkedin.com", resolved)

    def test_all_curated_jobs_have_zero_linkedin_urls(self):
        import json
        for path in ["data/jobs_export.json", "data/verified_jobs.json"]:
            with open(path, "r", encoding="utf-8") as f:
                jobs = json.load(f)
            for j in jobs:
                url = j.get("url") or j.get("apply_url") or ""
                self.assertNotIn("linkedin.com", url, f"Job {j.get('id')} ({j.get('company')}) has LinkedIn URL in {path}")
                self.assertNotIn("adzuna.", url, f"Job {j.get('id')} ({j.get('company')}) has Adzuna URL in {path}")

    def test_apply_redirect_for_various_employers(self):
        test_cases = [
            (4, "deloitte.com"),
            (6, "uber.com"),
            (9, "goldmansachs.tal.net"),
            (15, "myworkdayjobs.com"),
            (27, "jpmorgan.com"),
            (30, "pwc.com"),
            (35, "oracle.com"),
        ]
        for jid, expected_domain in test_cases:
            resp = self.client.get(f"/jobs/{jid}/apply", follow_redirects=False)
            self.assertEqual(resp.status_code, 302, f"Job {jid} apply redirect failed")
            loc = resp.headers.get("Location") or ""
            self.assertIn(expected_domain, loc, f"Job {jid} did not redirect to {expected_domain}, got {loc}")
            self.assertNotIn("linkedin.com", loc, f"Job {jid} unexpectedly redirected to LinkedIn")

if __name__ == "__main__":
    unittest.main()
