"""
==========================================================
Unit Tests for Multi-Source ATS Job Engine:
- Job Repository (SQLite discovered_jobs table)
- ATS Connectors (Greenhouse, Lever, Ashby, SmartRecruiters, Workable)
- URL Verifier & Origin Validator
- Multi-Source Synchronizer (sync_jobs)
==========================================================
"""

import unittest
import sqlite3
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from repositories.job_repository import (
    initialize_jobs_table,
    save_job,
    get_discovered_jobs,
    get_discovered_job_by_id,
    mark_job_verified,
    mark_job_closed,
)
from services.job_sources.connectors import (
    normalize_job,
    clean_html_text,
    fetch_greenhouse,
    fetch_lever,
    fetch_ashby,
    fetch_smartrecruiters,
    fetch_workable,
    CONNECTORS,
)
from services.job_sources.url_verifier import (
    verify_ats_origin,
    verify_destination_url,
    verify_job_destination,
)
from services.job_sources.sync_jobs import sync_all_companies


class TestJobRepository(unittest.TestCase):
    def setUp(self):
        import gc
        gc.collect()
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "test_jobs.db"
        initialize_jobs_table(str(self.db_path))

    def tearDown(self):
        import gc
        gc.collect()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_initialize_table(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='discovered_jobs'")
            self.assertIsNotNone(cursor.fetchone())

    def test_save_and_retrieve_job(self):
        job = {
            "company_name": "Test Company",
            "provider": "greenhouse",
            "company_key": "testcorp",
            "external_job_id": "990123",
            "job_title": "Senior Python Engineer",
            "location": "Bangalore, India",
            "official_job_url": "https://boards.greenhouse.io/testcorp/jobs/990123",
            "apply_url": "https://boards.greenhouse.io/testcorp/jobs/990123#app",
            "description": "Building scalable backend pipelines",
            "posted_at": "2026-10-17T12:00:00Z",
            "url_verified": True,
        }
        with sqlite3.connect(str(self.db_path)) as conn:
            saved = save_job(conn, job)
            self.assertTrue(saved)

        jobs = get_discovered_jobs(conn_or_path=self.db_path)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "Test Company")
        self.assertEqual(jobs[0]["provider"], "greenhouse")
        self.assertEqual(jobs[0]["external_job_id"], "990123")
        self.assertTrue(jobs[0]["url_verified"])

    def test_save_job_update_on_conflict(self):
        job1 = {
            "company_name": "Acme",
            "provider": "ashby",
            "company_key": "acme",
            "external_job_id": "req-1",
            "job_title": "Junior Engineer",
            "official_job_url": "https://jobs.ashbyhq.com/acme/req-1",
        }
        job2 = {
            "company_name": "Acme",
            "provider": "ashby",
            "company_key": "acme",
            "external_job_id": "req-1",
            "job_title": "Senior Engineer",
            "official_job_url": "https://jobs.ashbyhq.com/acme/req-1",
        }
        with sqlite3.connect(str(self.db_path)) as conn:
            save_job(conn, job1)
            save_job(conn, job2)

        jobs = get_discovered_jobs(conn_or_path=self.db_path)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "Senior Engineer")

    def test_get_discovered_job_by_id(self):
        job = {
            "company_name": "Linear",
            "provider": "ashby",
            "company_key": "linear",
            "external_job_id": "lin-777",
            "job_title": "Fullstack Engineer",
            "official_job_url": "https://jobs.ashbyhq.com/linear/lin-777",
        }
        with sqlite3.connect(str(self.db_path)) as conn:
            save_job(conn, job)

        found = get_discovered_job_by_id("lin-777", conn_or_path=self.db_path)
        self.assertIsNotNone(found)
        self.assertEqual(found["company"], "Linear")

    def test_mark_job_verified_and_closed(self):
        job = {
            "company_name": "Stripe",
            "provider": "greenhouse",
            "company_key": "stripe",
            "external_job_id": "str-42",
            "job_title": "Backend Engineer",
            "official_job_url": "https://boards.greenhouse.io/stripe/jobs/str-42",
            "url_verified": False,
        }
        with sqlite3.connect(str(self.db_path)) as conn:
            save_job(conn, job)

        mark_job_verified("str-42", verified=True, conn_or_path=self.db_path)
        updated = get_discovered_job_by_id("str-42", conn_or_path=self.db_path)
        self.assertTrue(updated["url_verified"])

        mark_job_closed("greenhouse", "stripe", "str-42", conn_or_path=self.db_path)
        open_jobs = get_discovered_jobs(conn_or_path=self.db_path, status="open")
        self.assertEqual(len(open_jobs), 0)


class TestATSConnectors(unittest.TestCase):
    def test_clean_html_text(self):
        raw = "<p>Join <strong>Google</strong> as a <em>Software Engineer</em></p>"
        self.assertEqual(clean_html_text(raw), "Join Google as a Software Engineer")

    def test_normalize_job(self):
        norm = normalize_job(
            company="Figma",
            provider="greenhouse",
            company_key="figma",
            job_id="12345",
            title="Product Designer",
            location="San Francisco, CA",
            job_url="https://boards.greenhouse.io/figma/jobs/12345",
            apply_url="https://boards.greenhouse.io/figma/jobs/12345#app",
            description="<p>Designing tools</p>",
        )
        self.assertEqual(norm["company"], "Figma")
        self.assertEqual(norm["provider"], "greenhouse")
        self.assertEqual(norm["external_job_id"], "12345")
        self.assertEqual(norm["description"], "Designing tools")
        self.assertEqual(norm["apply_url"], "https://boards.greenhouse.io/figma/jobs/12345#app")

    @patch("services.job_sources.connectors.get_json")
    def test_fetch_greenhouse(self, mock_get):
        mock_get.return_value = {
            "jobs": [
                {
                    "id": 101,
                    "title": "Backend Developer",
                    "location": {"name": "Remote"},
                    "absolute_url": "https://boards.greenhouse.io/gitlab/jobs/101",
                    "content": "<p>Build GitLab</p>",
                    "updated_at": "2026-10-17T00:00:00Z",
                }
            ]
        }
        config = {"company": "GitLab", "provider": "greenhouse", "board_token": "gitlab"}
        results = list(fetch_greenhouse(config))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["company"], "GitLab")
        self.assertEqual(results[0]["title"], "Backend Developer")
        self.assertEqual(results[0]["apply_url"], "https://boards.greenhouse.io/gitlab/jobs/101#app")

    @patch("services.job_sources.connectors.get_json")
    def test_fetch_lever(self, mock_get):
        mock_get.return_value = [
            {
                "id": "lev-505",
                "text": "Data Platform Engineer",
                "categories": {"location": "Stockholm"},
                "hostedUrl": "https://jobs.lever.co/spotify/lev-505",
                "applyUrl": "https://jobs.lever.co/spotify/lev-505/apply",
                "descriptionPlain": "Build streaming data systems",
                "createdAt": 1729100000000,
            }
        ]
        config = {"company": "Spotify", "provider": "lever", "site": "spotify"}
        results = list(fetch_lever(config))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Data Platform Engineer")
        self.assertEqual(results[0]["location"], "Stockholm")

    @patch("services.job_sources.connectors.get_json")
    def test_fetch_ashby(self, mock_get):
        mock_get.return_value = {
            "jobs": [
                {
                    "id": "ash-303",
                    "title": "Core Infrastructure Engineer",
                    "location": "Remote, Global",
                    "jobUrl": "https://jobs.ashbyhq.com/linear/ash-303",
                    "applyUrl": "https://jobs.ashbyhq.com/linear/ash-303/application",
                    "descriptionPlain": "Build Linear sync engine",
                    "publishedAt": "2026-10-17T09:00:00Z",
                }
            ]
        }
        config = {"company": "Linear", "provider": "ashby", "board_name": "linear"}
        results = list(fetch_ashby(config))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Core Infrastructure Engineer")
        self.assertEqual(results[0]["apply_url"], "https://jobs.ashbyhq.com/linear/ash-303/application")

    @patch("services.job_sources.connectors.get_json")
    def test_fetch_smartrecruiters(self, mock_get):
        mock_get.return_value = {
            "content": [
                {
                    "id": "sr-111",
                    "name": "Software Test Engineer",
                    "location": {"city": "Austin", "country": "US"},
                    "refNumber": "REF111A",
                    "releasedDate": "2026-10-16",
                }
            ]
        }
        config = {"company": "Visa", "provider": "smartrecruiters", "company_id": "Visa"}
        results = list(fetch_smartrecruiters(config))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Software Test Engineer")
        self.assertIn("Austin", results[0]["location"])

    @patch("services.job_sources.connectors.get_json")
    def test_fetch_workable(self, mock_get):
        mock_get.return_value = {
            "jobs": [
                {
                    "shortcode": "WRK01",
                    "title": "Frontend Engineer",
                    "city": "London",
                    "country": "UK",
                    "url": "https://apply.workable.com/testcorp/j/WRK01/",
                    "application_url": "https://apply.workable.com/testcorp/j/WRK01/apply/",
                    "description": "Vue and TypeScript",
                    "published_on": "2026-10-15",
                }
            ]
        }
        config = {"company": "TestCorp", "provider": "workable", "account_subdomain": "testcorp"}
        results = list(fetch_workable(config))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Frontend Engineer")
        self.assertEqual(results[0]["apply_url"], "https://apply.workable.com/testcorp/j/WRK01/apply/")


class TestUrlVerifier(unittest.TestCase):
    def test_verify_ats_origin_valid(self):
        self.assertTrue(verify_ats_origin("https://boards.greenhouse.io/gitlab/jobs/123", "greenhouse"))
        self.assertTrue(verify_ats_origin("https://jobs.lever.co/spotify/456", "lever"))
        self.assertTrue(verify_ats_origin("https://jobs.ashbyhq.com/linear/789", "ashby"))
        self.assertTrue(verify_ats_origin("https://jobs.smartrecruiters.com/visa/999", "smartrecruiters"))
        self.assertTrue(verify_ats_origin("https://apply.workable.com/acme/j/123/", "workable"))

    def test_verify_ats_origin_invalid(self):
        self.assertFalse(verify_ats_origin("not_a_valid_url"))
        self.assertFalse(verify_ats_origin("ftp://files.example.com"))

    @patch("requests.head")
    def test_verify_destination_url_live(self, mock_head):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://boards.greenhouse.io/gitlab/jobs/123#app"
        mock_head.return_value = mock_resp

        res = verify_destination_url("https://boards.greenhouse.io/gitlab/jobs/123#app")
        self.assertTrue(res["is_verified"])
        self.assertFalse(res["is_closed"])
        self.assertEqual(res["status_code"], 200)

    @patch("requests.head")
    def test_verify_destination_url_closed(self, mock_head):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.url = "https://boards.greenhouse.io/gitlab/jobs/old-job"
        mock_head.return_value = mock_resp

        res = verify_destination_url("https://boards.greenhouse.io/gitlab/jobs/old-job")
        self.assertFalse(res["is_verified"])
        self.assertTrue(res["is_closed"])
        self.assertEqual(res["status_code"], 404)


class TestSyncJobs(unittest.TestCase):
    def setUp(self):
        import gc
        gc.collect()
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "test_sync.db"
        self.reg_path = Path(self.temp_dir.name) / "test_reg.json"

        with open(self.reg_path, "w", encoding="utf-8") as f:
            json.dump([
                {"company": "MockGreenhouse", "provider": "greenhouse", "board_token": "mockgh"},
                {"company": "UnsupportedATS", "provider": "unknown_ats"},
            ], f)

    def tearDown(self):
        import gc
        gc.collect()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    @patch("services.job_sources.connectors.get_json")
    def test_sync_all_companies(self, mock_get):
        mock_get.return_value = {
            "jobs": [
                {
                    "id": 901,
                    "title": "Software Engineer",
                    "location": {"name": "Hyderabad"},
                    "absolute_url": "https://boards.greenhouse.io/mockgh/jobs/901",
                }
            ]
        }
        res = sync_all_companies(
            db_path=str(self.db_path),
            registry_path=self.reg_path,
            max_per_company=5,
            verify_urls=False,
        )
        self.assertEqual(res["total_companies_registered"], 2)
        self.assertEqual(res["total_companies_polled"], 1)
        self.assertEqual(res["total_jobs_saved"], 1)
        self.assertIn("UnsupportedATS", res["errors"])

        jobs = get_discovered_jobs(conn_or_path=self.db_path)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "MockGreenhouse")


if __name__ == "__main__":
    unittest.main()
