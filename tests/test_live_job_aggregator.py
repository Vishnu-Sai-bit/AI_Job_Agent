"""
Unit tests for Multi-Portal Live Job Aggregator and Free API Configuration.
"""
import unittest

from services.jobs.live_job_aggregator import (
    get_providers_status_summary,
    aggregate_live_jobs,
    extract_skills_from_text,
    format_inr_salary,
)

class TestLiveJobAggregator(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()
