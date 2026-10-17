"""
Unit Tests for ATS Provider Adapters & Application Link Resolution
"""

import unittest
from services.job_links.normalizer import (
    basic_url_check,
    verify_ats_domain,
    normalize_job,
    APPROVED_ATS_DOMAINS
)
from services.job_links.adapters.greenhouse import GreenhouseAdapter
from services.job_links.adapters.lever import LeverAdapter
from services.job_links.adapters.ashby import AshbyAdapter
from services.job_links.adapters.workday import WorkdayAdapter
from services.job_links.adapters.smartrecruiters import SmartRecruitersAdapter
from services.job_links.registry import detect_ats_provider, resolve_verified_apply_link
from app import create_app

class TestATSAdapters(unittest.TestCase):

    def test_basic_url_check(self):
        self.assertTrue(basic_url_check("https://boards.greenhouse.io/gitlab/jobs/12345"))
        self.assertTrue(basic_url_check("http://jobs.lever.co/postman/67890"))
        self.assertFalse(basic_url_check(""))
        self.assertFalse(basic_url_check("not-a-url"))
        self.assertFalse(basic_url_check("ftp://some.server/path"))

    def test_verify_ats_domain(self):
        self.assertTrue(verify_ats_domain("https://boards.greenhouse.io/gitlab/jobs/123"))
        self.assertTrue(verify_ats_domain("https://jobs.lever.co/postman/456"))
        self.assertTrue(verify_ats_domain("https://jobs.ashbyhq.com/huggingface/789"))
        self.assertTrue(verify_ats_domain("https://qualcomm.wd5.myworkdayjobs.com/External/job/101"))
        self.assertTrue(verify_ats_domain("https://jobs.smartrecruiters.com/Swiggy/202"))
        self.assertFalse(verify_ats_domain("https://random-unapproved-site.com/jobs/1"))

    def test_detect_ats_provider(self):
        self.assertEqual(detect_ats_provider("https://boards.greenhouse.io/stripe/jobs/1"), "Greenhouse")
        self.assertEqual(detect_ats_provider("https://jobs.lever.co/spotify/abc"), "Lever")
        self.assertEqual(detect_ats_provider("https://jobs.ashbyhq.com/zapier/def"), "Ashby")
        self.assertEqual(detect_ats_provider("https://salesforce.wd12.myworkdayjobs.com/Careers"), "Workday")
        self.assertEqual(detect_ats_provider("https://jobs.smartrecruiters.com/Swiggy/ghi"), "SmartRecruiters")
        self.assertEqual(detect_ats_provider("https://careers.google.com/jobs/results/123"), "Google Careers")
        self.assertEqual(detect_ats_provider("https://unknown-domain.com/job/123"), "Company Career Portal")

    def test_greenhouse_adapter(self):
        sample_item = {
            "id": 5829104,
            "title": "Senior Data Analyst",
            "absolute_url": "https://boards.greenhouse.io/gitlab/jobs/5829104",
            "location": {"name": "Remote"}
        }
        res = GreenhouseAdapter.parse_job(sample_item, company_name="GitLab")
        self.assertEqual(res["ats_provider"], "Greenhouse")
        self.assertEqual(res["external_job_id"], "5829104")
        self.assertEqual(res["official_job_url"], "https://boards.greenhouse.io/gitlab/jobs/5829104")
        self.assertEqual(res["apply_url"], "https://boards.greenhouse.io/gitlab/jobs/5829104#app")
        self.assertTrue(res["url_verified"])

    def test_lever_adapter(self):
        sample_item = {
            "id": "a1b2c3-d4e5",
            "text": "Product Data Analyst",
            "hostedUrl": "https://jobs.lever.co/postman/a1b2c3-d4e5",
            "applyUrl": "https://jobs.lever.co/postman/a1b2c3-d4e5/apply",
            "categories": {"location": "Bengaluru"}
        }
        res = LeverAdapter.parse_job(sample_item, company_name="Postman")
        self.assertEqual(res["ats_provider"], "Lever")
        self.assertEqual(res["external_job_id"], "a1b2c3-d4e5")
        self.assertEqual(res["official_job_url"], "https://jobs.lever.co/postman/a1b2c3-d4e5")
        self.assertEqual(res["apply_url"], "https://jobs.lever.co/postman/a1b2c3-d4e5/apply")
        self.assertTrue(res["url_verified"])

    def test_ashby_adapter(self):
        sample_item = {
            "id": "ash-7890",
            "title": "AI Research Analyst",
            "jobUrl": "https://jobs.ashbyhq.com/huggingface/ash-7890",
            "applyUrl": "https://jobs.ashbyhq.com/huggingface/ash-7890/application",
            "location": "Remote"
        }
        res = AshbyAdapter.parse_job(sample_item, company_name="Hugging Face")
        self.assertEqual(res["ats_provider"], "Ashby")
        self.assertEqual(res["external_job_id"], "ash-7890")
        self.assertEqual(res["official_job_url"], "https://jobs.ashbyhq.com/huggingface/ash-7890")
        self.assertEqual(res["apply_url"], "https://jobs.ashbyhq.com/huggingface/ash-7890/application")
        self.assertTrue(res["url_verified"])

    def test_workday_adapter_special_rule(self):
        # Rule: Do not manufacture URLs by appending requisition IDs to myworkdayjobs.com.
        # Must preserve exact posting URL.
        posting_url = "https://qualcomm.wd5.myworkdayjobs.com/External/job/Hyderabad/Python-Automation-Tools-Engineer_JR-4442985376"
        res = WorkdayAdapter.parse_job(
            official_posting_url=posting_url,
            company_name="Qualcomm",
            job_title="Python Automation & Tools Engineer",
            location="Hyderabad"
        )
        self.assertEqual(res["ats_provider"], "Workday")
        self.assertEqual(res["external_job_id"], "JR-4442985376")
        self.assertEqual(res["official_job_url"], posting_url)
        self.assertEqual(res["apply_url"], posting_url + "/apply")
        self.assertTrue(res["url_verified"])

    def test_smartrecruiters_adapter(self):
        sample_item = {
            "id": "743999981234567",
            "name": "Data Analyst - Growth",
            "ref": "https://jobs.smartrecruiters.com/Swiggy/743999981234567-data-analyst",
            "location": {"city": "Bangalore"}
        }
        res = SmartRecruitersAdapter.parse_job(sample_item, company_name="Swiggy", company_id="Swiggy")
        self.assertEqual(res["ats_provider"], "SmartRecruiters")
        self.assertEqual(res["external_job_id"], "743999981234567")
        self.assertEqual(res["official_job_url"], sample_item["ref"])
        self.assertEqual(res["apply_url"], "https://jobs.smartrecruiters.com/Swiggy/743999981234567/apply")
        self.assertTrue(res["url_verified"])

    def test_resolve_verified_apply_link_fallback_hierarchy(self):
        # 1. Verified direct application link prioritized
        job1 = {
            "ats_provider": "Greenhouse",
            "official_job_url": "https://boards.greenhouse.io/gitlab/jobs/123",
            "apply_url": "https://boards.greenhouse.io/gitlab/jobs/123#app",
            "job_status": "open"
        }
        r1 = resolve_verified_apply_link(job1)
        self.assertTrue(r1["can_apply"])
        self.assertEqual(r1["type"], "direct_application")
        self.assertEqual(r1["destination_url"], "https://boards.greenhouse.io/gitlab/jobs/123#app")

        # 2. Falls back to verified official job detail URL if apply_url empty
        job2 = {
            "ats_provider": "Workday",
            "official_job_url": "https://qualcomm.wd5.myworkdayjobs.com/External/job/Hyderabad/123",
            "apply_url": "",
            "job_status": "open"
        }
        r2 = resolve_verified_apply_link(job2)
        self.assertTrue(r2["can_apply"])
        self.assertEqual(r2["type"], "job_detail")
        self.assertEqual(r2["destination_url"], "https://qualcomm.wd5.myworkdayjobs.com/External/job/Hyderabad/123")

        # 3. Closed job cannot be applied to
        job3 = {
            "ats_provider": "Lever",
            "official_job_url": "https://jobs.lever.co/postman/123",
            "apply_url": "https://jobs.lever.co/postman/123/apply",
            "job_status": "closed"
        }
        r3 = resolve_verified_apply_link(job3)
        self.assertFalse(r3["can_apply"])

        # 4. Unverified job link returns can_apply=False
        job4 = {
            "official_job_url": "",
            "apply_url": ""
        }
        r4 = resolve_verified_apply_link(job4)
        self.assertFalse(r4["can_apply"])
        self.assertIsNone(r4["destination_url"])

    def test_apply_redirect_flask_route(self):
        app = create_app()
        client = app.test_client()

        # Job 1 in jobs_export.json is Google with verified apply URL
        response = client.get("/jobs/1/apply")
        self.assertEqual(response.status_code, 302)
        self.assertIn("careers.google.com", response.headers["Location"])

        # Job 7 in jobs_export.json is Razorpay on Greenhouse
        response2 = client.get("/jobs/7/apply")
        self.assertEqual(response2.status_code, 302)
        self.assertIn("boards.greenhouse.io/razorpay", response2.headers["Location"])

if __name__ == "__main__":
    unittest.main()
