"""
Unit tests for Tier 1 and Tier 2 ATS Connectors:
Workday, Greenhouse, Lever, Ashby, SmartRecruiters, Workable,
Teamtailor, Recruitee, Personio, BambooHR, Pinpoint, Breezy,
Jobvite, JazzHR, SAP SuccessFactors, Taleo, iCIMS, UKG, Cornerstone.
"""

import unittest
from unittest.mock import patch, MagicMock
from services.job_sources.connectors import (
    CONNECTORS,
    fetch_workday,
    fetch_greenhouse,
    fetch_lever,
    fetch_ashby,
    fetch_smartrecruiters,
    fetch_workable,
    fetch_teamtailor,
    fetch_recruitee,
    fetch_personio,
    fetch_bamboohr,
    fetch_pinpoint,
    fetch_breezy,
    fetch_jobvite,
    fetch_jazzhr,
    fetch_successfactors,
    fetch_taleo,
    fetch_icims,
    fetch_ukg,
    fetch_cornerstone,
)


class TestATSConnectors(unittest.TestCase):

    def test_all_19_connectors_registered(self):
        expected_providers = [
            # Tier 1
            "greenhouse", "lever", "ashby", "smartrecruiters", "workable",
            "workday", "teamtailor", "recruitee", "personio",
            # Tier 2
            "bamboohr", "pinpoint", "breezy", "jobvite", "jazzhr",
            "successfactors", "taleo", "icims", "ukg", "cornerstone"
        ]
        for p in expected_providers:
            self.assertIn(p, CONNECTORS, f"Connector '{p}' must be registered in CONNECTORS")

    @patch("requests.post")
    def test_fetch_workday_cxs_api(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "jobPostings": [
                {
                    "title": "Software Engineer III",
                    "externalPath": "/job/Bangalore/Software-Engineer_R123456",
                    "bulletFields": ["R123456", "Bangalore, India"],
                    "locationsText": "Bangalore, India",
                    "postedOn": "2026-10-17"
                }
            ]
        }
        mock_post.return_value = mock_resp

        config = {
            "company": "Cisco",
            "tenant": "cisco",
            "domain": "cisco.wd5.myworkdayjobs.com",
            "site": "External"
        }
        jobs = list(fetch_workday(config))
        self.assertEqual(len(jobs), 1)
        j = jobs[0]
        self.assertEqual(j["company"], "Cisco")
        self.assertEqual(j["provider"], "workday")
        self.assertEqual(j["external_job_id"], "R123456")
        self.assertIn("cisco.wd5.myworkdayjobs.com", j["job_url"])
        self.assertIn("/apply", j["apply_url"])

    @patch("services.job_sources.connectors.get_json")
    def test_fetch_recruitee_api(self, mock_get_json):
        mock_get_json.return_value = {
            "offers": [
                {
                    "id": 889900,
                    "title": "Senior Data Analyst",
                    "careers_url": "https://hotjar.recruitee.com/o/senior-data-analyst",
                    "careers_apply_url": "https://hotjar.recruitee.com/o/senior-data-analyst/apply",
                    "location": "Remote, Global",
                    "description": "Analyze key customer trends and product telemetry.",
                    "published_at": "2026-10-17"
                }
            ]
        }
        config = {
            "company": "Hotjar",
            "subdomain": "hotjar"
        }
        jobs = list(fetch_recruitee(config))
        self.assertEqual(len(jobs), 1)
        j = jobs[0]
        self.assertEqual(j["company"], "Hotjar")
        self.assertEqual(j["provider"], "recruitee")
        self.assertEqual(j["external_job_id"], "889900")
        self.assertEqual(j["apply_url"], "https://hotjar.recruitee.com/o/senior-data-analyst/apply")

    @patch("services.job_sources.connectors.get_json")
    def test_fetch_bamboohr_api(self, mock_get_json):
        mock_get_json.return_value = {
            "result": [
                {
                    "id": "101",
                    "jobOpeningName": "Junior Python Developer",
                    "careerPageUrl": "https://jane.bamboohr.com/careers/101",
                    "location": {"city": "Remote", "state": "Global"}
                }
            ]
        }
        config = {
            "company": "Jane",
            "subdomain": "jane"
        }
        jobs = list(fetch_bamboohr(config))
        self.assertEqual(len(jobs), 1)
        j = jobs[0]
        self.assertEqual(j["company"], "Jane")
        self.assertEqual(j["provider"], "bamboohr")
        self.assertEqual(j["external_job_id"], "101")
        self.assertIn("jane.bamboohr.com", j["job_url"])

    @patch("services.job_sources.connectors.get_json")
    def test_fetch_pinpoint_api(self, mock_get_json):
        mock_get_json.return_value = {
            "data": [
                {
                    "id": "pin_456",
                    "title": "Infrastructure Engineer",
                    "url": "https://monzo.pinpointhq.com/postings/pin_456",
                    "apply_url": "https://monzo.pinpointhq.com/postings/pin_456/applications/new",
                    "location": "Remote"
                }
            ]
        }
        config = {
            "company": "Monzo",
            "subdomain": "monzo"
        }
        jobs = list(fetch_pinpoint(config))
        self.assertEqual(len(jobs), 1)
        j = jobs[0]
        self.assertEqual(j["company"], "Monzo")
        self.assertEqual(j["provider"], "pinpoint")
        self.assertEqual(j["external_job_id"], "pin_456")

    @patch("services.job_sources.connectors.get_json")
    def test_fetch_breezy_api(self, mock_get_json):
        mock_get_json.return_value = [
            {
                "id": "brz_789",
                "name": "Backend Architect",
                "url": "https://launchdarkly.breezy.hr/p/brz_789",
                "location": {"name": "Bengaluru"}
            }
        ]
        config = {
            "company": "LaunchDarkly",
            "subdomain": "launchdarkly"
        }
        jobs = list(fetch_breezy(config))
        self.assertEqual(len(jobs), 1)
        j = jobs[0]
        self.assertEqual(j["company"], "LaunchDarkly")
        self.assertEqual(j["provider"], "breezy")
        self.assertEqual(j["apply_url"], "https://launchdarkly.breezy.hr/p/brz_789/apply")

    def test_fetch_taleo_config(self):
        config = {
            "company": "Oracle",
            "company_key": "oracle",
            "jobs": [
                {
                    "id": "4436234941",
                    "title": "Cloud Solutions Architect",
                    "career_section": "2"
                }
            ]
        }
        jobs = list(fetch_taleo(config))
        self.assertEqual(len(jobs), 1)
        j = jobs[0]
        self.assertEqual(j["company"], "Oracle")
        self.assertEqual(j["provider"], "taleo")
        self.assertEqual(j["external_job_id"], "4436234941")
        self.assertIn("oracle.taleo.net", j["job_url"])

    def test_fetch_successfactors_config(self):
        config = {
            "company": "Siemens",
            "company_key": "siemens",
            "jobs": [
                {
                    "id": "REQ-9988",
                    "title": "Industrial Automation Engineer"
                }
            ]
        }
        jobs = list(fetch_successfactors(config))
        self.assertEqual(len(jobs), 1)
        j = jobs[0]
        self.assertEqual(j["company"], "Siemens")
        self.assertEqual(j["provider"], "successfactors")
        self.assertEqual(j["external_job_id"], "REQ-9988")
        self.assertIn("career.successfactors.com", j["job_url"])


if __name__ == "__main__":
    unittest.main()
