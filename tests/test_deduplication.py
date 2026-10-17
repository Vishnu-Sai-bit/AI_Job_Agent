"""
Unit tests for the enterprise job deduplication engine.
"""

import unittest
from services.jobs.deduplicator import (
    normalize_canonical_company,
    normalize_canonical_title,
    normalize_canonical_url,
    extract_canonical_req_id,
    deduplicate_jobs,
)


class TestJobDeduplicator(unittest.TestCase):

    def test_normalize_canonical_company(self):
        self.assertEqual(normalize_canonical_company("Tata Consultancy Services (TCS)"), "tcs")
        self.assertEqual(normalize_canonical_company("EY (Ernst & Young)"), "ey")
        self.assertEqual(normalize_canonical_company("Google Inc."), "google")
        self.assertEqual(normalize_canonical_company("Razorpay Software Pvt Ltd"), "razorpay")
        self.assertEqual(normalize_canonical_company("Cisco Systems India Private Limited"), "cisco")

    def test_normalize_canonical_title(self):
        raw1 = "Software Engineer | Java/Golang/Python/ C/C++ | 2 to 4 years | Bangalore"
        self.assertEqual(normalize_canonical_title(raw1), "software engineer")

        raw2 = "[Hiring] Junior Data Analyst (Bangalore, India)"
        self.assertEqual(normalize_canonical_title(raw2), "junior data analyst")

        raw3 = "Lead Software Engineer - Mobile (Flutter) - Pune"
        self.assertEqual(normalize_canonical_title(raw3), "lead software engineer mobile")

    def test_normalize_canonical_url(self):
        url1 = "https://boards.greenhouse.io/razorpay/jobs/4495642497?utm_source=google#app"
        url2 = "https://boards.greenhouse.io/razorpay/jobs/4495642497/"
        self.assertEqual(normalize_canonical_url(url1), "boards.greenhouse.io/razorpay/jobs/4495642497")
        self.assertEqual(normalize_canonical_url(url1), normalize_canonical_url(url2))

    def test_deduplicate_jobs_by_canonical_title_and_company(self):
        jobs = [
            {
                "id": 1,
                "title": "Software Engineer | Python/SQL | 2-4 yrs | Bangalore",
                "company": "Cisco",
                "url": "https://cisco.wd5.myworkdayjobs.com/External/job/1"
            },
            {
                "id": 2,
                "title": "Software Engineer",
                "company": "Cisco Systems India",
                "url": "https://cisco.wd5.myworkdayjobs.com/External/job/2"
            },
            {
                "id": 3,
                "title": "Data Analyst",
                "company": "Google",
                "url": "https://careers.google.com/jobs/results/100"
            }
        ]
        unique = deduplicate_jobs(jobs)
        self.assertEqual(len(unique), 2)
        self.assertEqual(unique[0]["id"], 1)
        self.assertEqual(unique[1]["id"], 3)

    def test_deduplicate_jobs_by_url(self):
        jobs = [
            {
                "id": 10,
                "title": "Data Analyst - Growth",
                "company": "Razorpay",
                "url": "https://boards.greenhouse.io/razorpay/jobs/999?utm_campaign=feed"
            },
            {
                "id": 11,
                "title": "Analyst - Marketing",
                "company": "Razorpay",
                "url": "https://boards.greenhouse.io/razorpay/jobs/999#app"
            }
        ]
        unique = deduplicate_jobs(jobs)
        self.assertEqual(len(unique), 1)

    def test_deduplicate_jobs_by_req_id(self):
        jobs = [
            {
                "id": 21,
                "external_job_id": "REQ-778899",
                "title": "Associate Renewals Manager - EMEA",
                "company": "GitLab",
                "url": "https://job-boards.greenhouse.io/gitlab/jobs/1"
            },
            {
                "id": 22,
                "external_job_id": "REQ-778899",
                "title": "Associate Renewals Manager - US",
                "company": "GitLab",
                "url": "https://job-boards.greenhouse.io/gitlab/jobs/2"
            }
        ]
        unique = deduplicate_jobs(jobs)
        self.assertEqual(len(unique), 1)


if __name__ == "__main__":
    unittest.main()
