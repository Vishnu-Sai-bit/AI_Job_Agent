"""
==========================================================
Unit Tests for AI Job Agent Blueprint Architecture
Verifies:
1. Collectors: Workday, Greenhouse, Lever, Company Careers,
   Remotive, RemoteOK, ArbeitNow
2. Job Normalizer (11 Canonical Fields & Zero Salary Display)
3. Multi-Factor Deduplication (URL, Company+ReqID, Company+Title+Loc)
4. Job Verifier (Direct Destination & Aggregator Blocking)
5. Resume-Based Job Matcher (Skills, Score 0-100%, Experience)
6. Unified Database Layer (Job Model & db.py Operations)
7. Templates (11 Fields Displayed & Zero Salary Exposure)
==========================================================
"""

import unittest
import tempfile
import json
from pathlib import Path

from collectors import (
    WorkdayCollector,
    GreenhouseCollector,
    LeverCollector,
    CompanyCareersCollector,
    RemotiveCollector,
    RemoteOKCollector,
    ArbeitNowCollector,
    ALL_COLLECTORS,
)
from services.job_normalizer import normalize_job_dict, normalize_job_list
from services.deduplication import deduplicate_jobs, canonicalize_url
from services.job_verifier import verify_job_listing, JobVerifier
from services.job_matcher import match_and_rank_jobs, JobMatcher
from database.models import Job
from database.db import init_db, save_job, get_all_jobs, get_job_by_id, update_job_status


class TestBlueprintArchitecture(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.test_db_path = Path(self.temp_dir.name) / "test_blueprint.db"
        init_db(self.test_db_path)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    # 1. Collectors Test
    def test_collectors_instantiation(self):
        self.assertGreaterEqual(len(ALL_COLLECTORS), 7)
        for col_cls in ALL_COLLECTORS:
            col = col_cls()
            self.assertTrue(hasattr(col, "fetch_jobs"))
            self.assertTrue(hasattr(col, "name"))

    def test_company_careers_collector(self):
        col = CompanyCareersCollector()
        jobs = col.fetch_jobs(limit=5)
        self.assertIsInstance(jobs, list)
        if jobs:
            j = jobs[0]
            self.assertIn("job_id", j)
            self.assertIn("company_name", j)
            self.assertIn("apply_url", j)
            self.assertNotIn("salary", j)

    # 2. Normalizer & Zero Salary
    def test_normalizer_11_fields_and_zero_salary(self):
        raw = {
            "title": "Lead Data Analyst",
            "company": "Target",
            "description": "<p>Responsible for SQL data modeling and insights.</p>",
            "location": "Bengaluru",
            "url": "https://target.wd5.myworkdayjobs.com/targetcareers/job/R0001",
            "id": "R0001",
            "salary": "$120,000 - $140,000",
            "compensation": "High base",
            "wage": "Hourly"
        }
        normalized = normalize_job_dict(raw, default_source="Workday")

        # Required 11 canonical fields
        required_11 = [
            "job_id", "company_name", "job_title", "description",
            "location", "posted_at", "source_platform", "original_url",
            "apply_url", "last_verified_at", "status"
        ]
        for field in required_11:
            self.assertIn(field, normalized, f"Missing required field: {field}")

        self.assertEqual(normalized["job_id"], "R0001")
        self.assertEqual(normalized["company_name"], "Target")
        self.assertEqual(normalized["job_title"], "Lead Data Analyst")
        self.assertEqual(normalized["description"], "Responsible for SQL data modeling and insights.")
        self.assertEqual(normalized["status"], "active")

        # STRICT: Zero salary or compensation keys retained
        self.assertNotIn("salary", normalized)
        self.assertNotIn("compensation", normalized)
        self.assertNotIn("wage", normalized)

    # 3. Multi-Factor Deduplication
    def test_multi_factor_deduplication(self):
        job1 = {
            "job_id": "REQ-101",
            "company_name": "Accenture",
            "job_title": "Packaged/SaaS Application Engineer",
            "location": "Bengaluru",
            "apply_url": "https://www.accenture.com/in-en/careers/jobdetails?id=ATCI-101&utm_source=test",
        }
        # Duplicate by URL (tracking params stripped)
        job2 = {
            "job_id": "REQ-DIFFERENT",
            "company_name": "Accenture",
            "job_title": "Packaged/SaaS Application Engineer",
            "location": "Bengaluru",
            "apply_url": "https://www.accenture.com/in-en/careers/jobdetails?id=ATCI-101",
        }
        # Duplicate by Company + Requisition ID
        job3 = {
            "job_id": "REQ-101",
            "company_name": "Accenture",
            "job_title": "Different Title",
            "location": "Hyderabad",
            "apply_url": "https://www.accenture.com/in-en/careers/other",
        }
        # Unique Job
        job4 = {
            "job_id": "REQ-202",
            "company_name": "Microsoft",
            "job_title": "Software Engineer",
            "location": "Hyderabad",
            "apply_url": "https://careers.microsoft.com/jobs/REQ-202",
        }

        unique = deduplicate_jobs([job1, job2, job3, job4])
        self.assertEqual(len(unique), 2)
        self.assertEqual(unique[0]["company_name"], "Accenture")
        self.assertEqual(unique[1]["company_name"], "Microsoft")

    # 4. Verifier & Aggregator Blocking
    def test_verifier_blocks_intermediate_aggregators(self):
        verifier = JobVerifier()
        # Direct Workday apply -> valid
        valid_job = {
            "apply_url": "https://target.wd5.myworkdayjobs.com/targetcareers/job/123",
            "job_title": "Analyst"
        }
        res_valid = verifier.verify_job(valid_job)
        self.assertTrue(res_valid["url_verified"])
        self.assertEqual(res_valid["status"], "active")

        # LinkedIn aggregator link -> blocked
        linkedin_job = {
            "apply_url": "https://www.linkedin.com/jobs/view/123456",
            "job_title": "Analyst"
        }
        res_li = verifier.verify_job(linkedin_job)
        self.assertFalse(res_li["url_verified"])
        self.assertEqual(res_li["status"], "aggregator_blocked")

    # 5. Resume Matcher
    def test_resume_matching_logic(self):
        matcher = JobMatcher(candidate_skills=["Python", "SQL", "Tableau"], candidate_role="Data Analyst")
        job = {
            "job_title": "Senior Data Analyst",
            "description": "Looking for SQL, Python, Tableau, and AWS expertise.",
            "skills": ["SQL", "Python", "Tableau", "AWS"]
        }
        matched = matcher.match_job(job)
        self.assertGreater(matched["match_score"], 60.0)
        self.assertIn("Python", matched["matching_skills"])
        self.assertIn("Sql", [s.capitalize() for s in matched["matching_skills"]])
        self.assertIn("Aws", [s.capitalize() for s in matched["missing_skills"]])
        self.assertTrue(bool(matched["experience_alignment"]))

    # 6. Database Operations (models.py & db.py)
    def test_database_persistence_and_queries(self):
        job = Job(
            job_id="ATCI-5816189",
            company_name="Accenture",
            job_title="Packaged/SaaS Application Engineer",
            description="Enterprise application implementation role.",
            location="Bengaluru",
            posted_at="2026-10-18T10:00:00Z",
            source_platform="Accenture Careers",
            original_url="https://www.accenture.com/in-en/careers/jobdetails?id=ATCI-5816189-S2072200_en",
            apply_url="https://www.accenture.com/in-en/careers/jobdetails?id=ATCI-5816189-S2072200_en",
            status="active",
            skills=["SAP", "Cloud", "APIs"],
            match_score=88.5
        )

        # Save
        saved = save_job(job, db_path=self.test_db_path)
        self.assertTrue(saved)

        # Get by ID
        fetched = get_job_by_id("ATCI-5816189", db_path=self.test_db_path)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.company_name, "Accenture")
        self.assertEqual(fetched.job_id, "ATCI-5816189")
        self.assertEqual(fetched.match_score, 88.5)
        self.assertEqual(fetched.salary, "")  # Zero salary check

        # Update status
        updated = update_job_status("ATCI-5816189", "closed", db_path=self.test_db_path)
        self.assertTrue(updated)
        fetched_after = get_job_by_id("ATCI-5816189", db_path=self.test_db_path)
        self.assertEqual(fetched_after.status, "closed")

    # 7. Templates Zero Salary Inspection
    def test_templates_content_and_zero_salary(self):
        template_dir = Path(__file__).resolve().parents[1] / "templates"
        for t_name in ["index.html", "jobs.html", "job_details.html"]:
            t_file = template_dir / t_name
            self.assertTrue(t_file.exists(), f"Template missing: {t_name}")
            with open(t_file, "r", encoding="utf-8") as f:
                content = f.read().lower()
                self.assertNotIn("{{ job.salary }}", content)
                self.assertNotIn("salary:", content)
                self.assertNotIn("ctc", content)
                self.assertNotIn("compensation", content)


if __name__ == "__main__":
    unittest.main()
