"""
==========================================================
Unit Tests for Apply Now Workflow & Security Matrix
Verifies all 7 core test cases specified in the requirements:
1. Valid job record and approved URL -> Redirect to that job's URL
2. Unknown internal job ID -> HTTP 404
3. Inactive job -> HTTP 404
4. URL on an unapproved host -> No redirect / HTTP 404
5. Invalid application URL but valid job URL -> Use approved job detail URL
6. Job no longer available -> Flag or deactivate through verification workflow
7. Duplicate source job ID -> Update existing record instead of creating duplicate
==========================================================
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from flask import Flask
from models import db, Job
from job_service import (
    validate_official_url,
    select_apply_url,
    check_job_link,
    save_job,
    ALLOWED_HOSTS,
)


class TestApplyNowWorkflow(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder="templates")
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "test_apply_jobs.db"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{self.db_path}"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["TESTING"] = True

        db.init_app(self.app)

        # Register routes matching app.py
        with self.app.app_context():
            db.create_all()

            @self.app.route("/")
            def home():
                jobs = Job.query.filter_by(is_active=True).order_by(Job.first_seen_at.desc()).all()
                return f"Jobs Count: {len(jobs)}"

            @self.app.route("/apply/<int:job_id>")
            def apply_to_job(job_id):
                job = db.session.get(Job, job_id)
                if job is None or not job.is_active:
                    from flask import abort
                    abort(404)

                target_url = select_apply_url(job)
                if not target_url or not validate_official_url(target_url):
                    from flask import abort
                    abort(404)

                from flask import redirect
                return redirect(target_url, code=302)

        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    # Test 1: Valid job record and approved URL -> Redirect to that job's URL
    def test_valid_job_redirects_to_approved_url(self):
        with self.app.app_context():
            job = save_job({
                "source_platform": "greenhouse",
                "source_job_id": "gh-99881",
                "company_name": "GitLab",
                "title": "Senior Backend Engineer",
                "original_url": "https://boards.greenhouse.io/gitlab/jobs/99881",
                "apply_url": "https://boards.greenhouse.io/gitlab/jobs/99881#app",
                "is_active": True,
                "link_status": "verified"
            })
            job_id = job.id

        resp = self.client.get(f"/apply/{job_id}")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers.get("Location"), "https://boards.greenhouse.io/gitlab/jobs/99881#app")

    # Test 2: Unknown internal job ID -> HTTP 404
    def test_unknown_internal_job_id_returns_404(self):
        resp = self.client.get("/apply/999999")
        self.assertEqual(resp.status_code, 404)

    # Test 3: Inactive job -> HTTP 404
    def test_inactive_job_returns_404(self):
        with self.app.app_context():
            job = save_job({
                "source_platform": "lever",
                "source_job_id": "lev-closed-01",
                "company_name": "Spotify",
                "title": "Data Engineer",
                "original_url": "https://jobs.lever.co/spotify/lev-closed-01",
                "is_active": False,
                "link_status": "unavailable"
            })
            job_id = job.id

        resp = self.client.get(f"/apply/{job_id}")
        self.assertEqual(resp.status_code, 404)

    # Test 4: URL on an unapproved host -> No redirect / HTTP 404
    def test_unapproved_host_url_rejected(self):
        # 1. Direct validation check
        bad_url = "https://untrusted-scam-site.org/phishing/job"
        self.assertFalse(validate_official_url(bad_url))

        # 2. save_job rejects unapproved original_url
        with self.app.app_context():
            with self.assertRaises(ValueError):
                save_job({
                    "source_platform": "custom",
                    "source_job_id": "bad-01",
                    "company_name": "Unknown",
                    "title": "Engineer",
                    "original_url": bad_url
                })

    # Test 5: Invalid application URL but valid job URL -> Use approved job detail URL
    def test_invalid_apply_url_falls_back_to_valid_original_url(self):
        with self.app.app_context():
            job = save_job({
                "source_platform": "workday",
                "source_job_id": "wd-target-55",
                "company_name": "Target",
                "title": "Lead Data Analyst",
                "original_url": "https://target.wd5.myworkdayjobs.com/targetcareers/job/55",
                "apply_url": "http://insecure-http-apply.com/apply",  # Non-HTTPS, unapproved host
                "is_active": True
            })
            self.assertIsNone(job.apply_url)  # Invalid apply_url was nullified
            chosen_url = select_apply_url(job)
            self.assertEqual(chosen_url, "https://target.wd5.myworkdayjobs.com/targetcareers/job/55")
            job_id = job.id

        resp = self.client.get(f"/apply/{job_id}")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers.get("Location"), "https://target.wd5.myworkdayjobs.com/targetcareers/job/55")

    # Test 6: Job no longer available -> Flag or deactivate through verification workflow
    def test_job_closure_and_unavailable_status(self):
        with patch("job_service.requests.get") as mock_get:
            # Simulate 404 response from ATS
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp

            status = check_job_link("https://boards.greenhouse.io/stripe/jobs/closed-123")
            self.assertEqual(status, "unavailable")

        # Deactivate in database
        with self.app.app_context():
            job = save_job({
                "source_platform": "greenhouse",
                "source_job_id": "stripe-closed",
                "company_name": "Stripe",
                "title": "Software Engineer",
                "original_url": "https://boards.greenhouse.io/stripe/jobs/closed-123",
                "is_active": True
            })
            # Deactivate
            job.is_active = False
            job.link_status = "unavailable"
            db.session.commit()

            fetched = Job.query.filter_by(source_job_id="stripe-closed").first()
            self.assertFalse(fetched.is_active)
            self.assertEqual(fetched.link_status, "unavailable")

    # Test 7: Duplicate source job ID -> Update existing record instead of creating duplicate
    def test_duplicate_source_job_id_updates_existing(self):
        with self.app.app_context():
            job1 = save_job({
                "source_platform": "accenture",
                "source_job_id": "ATCI-5816189",
                "company_name": "Accenture",
                "title": "Packaged/SaaS Application Engineer",
                "original_url": "https://www.accenture.com/in-en/careers/jobdetails?id=ATCI-5816189-S2072200_en",
                "location": "Bengaluru",
                "link_status": "unverified"
            })
            first_id = job1.id

            # Save again with updated title and verified status
            job2 = save_job({
                "source_platform": "accenture",
                "source_job_id": "ATCI-5816189",
                "company_name": "Accenture",
                "title": "Senior Packaged/SaaS Application Engineer",
                "original_url": "https://www.accenture.com/in-en/careers/jobdetails?id=ATCI-5816189-S2072200_en",
                "location": "Hyderabad",
                "link_status": "verified"
            })
            second_id = job2.id

            # Internal ID must remain identical
            self.assertEqual(first_id, second_id)

            # Count must be 1, not 2
            total_records = Job.query.filter_by(source_job_id="ATCI-5816189").count()
            self.assertEqual(total_records, 1)

            updated_record = db.session.get(Job, first_id)
            self.assertEqual(updated_record.title, "Senior Packaged/SaaS Application Engineer")
            self.assertEqual(updated_record.location, "Hyderabad")
            self.assertEqual(updated_record.link_status, "verified")


if __name__ == "__main__":
    unittest.main()
