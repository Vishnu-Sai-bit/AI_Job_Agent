"""
Unit tests for Multi-Portal Live Job Aggregator and Free API Configuration.
"""
import unittest
from fastapi.testclient import TestClient
from app import app
from services.jobs.live_job_aggregator import (
    get_providers_status_summary,
    aggregate_live_jobs,
    extract_skills_from_text,
    format_inr_salary,
)

class TestLiveJobAggregator(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_providers_status_summary(self):
        providers = get_providers_status_summary()
        self.assertIsInstance(providers, list)
        names = [p["name"] for p in providers]
        self.assertTrue(any("LinkedIn" in n for n in names))
        self.assertTrue(any("Adzuna" in n for n in names))
        self.assertTrue(any("RemoteOK" in n for n in names))
        self.assertTrue(any("ArbeitNow" in n for n in names))
        self.assertTrue(any("Remotive" in n for n in names))
        self.assertTrue(any("Jobicy" in n for n in names))

    def test_extract_skills_from_text(self):
        text = "Looking for a Python Developer experienced in SQL, Pandas, and Tableau."
        skills = extract_skills_from_text(text, "Data Analyst")
        self.assertIn("Python", skills)
        self.assertIn("SQL", skills)
        self.assertIn("Pandas", skills)

    def test_format_inr_salary(self):
        sal = format_inr_salary(600000, 1200000)
        self.assertIn("LPA", sal)

    def test_api_providers_status_endpoint(self):
        response = self.client.get("/api/jobs/providers-status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("providers", data)
        self.assertIsInstance(data["providers"], list)

    def test_api_save_keys_endpoint(self):
        response = self.client.post("/api/jobs/save-api-keys", json={
            "adzuna_app_id": "01f60413",
            "adzuna_app_key": "84eadc4465099143ffc6cfe3db3f1f02"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("updated_keys", data)

    def test_api_search_live_jobs_endpoint(self):
        # Test with zero-key provider arbeitnow
        response = self.client.post("/api/jobs/search-live", json={
            "role": "Data Analyst",
            "location": "India",
            "sources": ["arbeitnow"],
            "candidate_skills": ["Python", "SQL", "Excel"],
            "max_total": 5
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("jobs", data)
        self.assertIn("sources_polled", data)

if __name__ == "__main__":
    unittest.main()
