"""
==========================================================
Unit & Integration Tests for AI Career Copilot Assistant
==========================================================
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.analytics.copilot_assistant import copilot_assistant

class TestCopilotAssistant(unittest.TestCase):

    def setUp(self):
        self.mock_resume = {
            "name": "Beere Vishnu Sai",
            "preferred_role": "Data Analyst",
            "skills": ["Python", "SQL", "Power BI", "Tableau", "Excel"],
            "ats_score": 88
        }
        self.mock_jobs = [
            {"title": "Junior Data Analyst", "company": "GlobalCorp", "location": "Hyderabad", "match_score": 92},
            {"title": "Data Analyst", "company": "Scout Inc", "location": "Hyderabad", "match_score": 89}
        ]

    def test_focus_jobs_query(self):
        res = copilot_assistant.answer_query(
            query="Which jobs should I focus on today?",
            resume_context=self.mock_resume,
            jobs=self.mock_jobs
        )
        self.assertTrue(res["success"])
        self.assertIn("GlobalCorp", res["response"])
        self.assertIn("suggested_actions", res)

    def test_ats_improvement_query(self):
        res = copilot_assistant.answer_query(
            query="How can I improve my ATS score and match rate?",
            resume_context=self.mock_resume
        )
        self.assertTrue(res["success"])
        self.assertIn("ATS", res["response"])
        self.assertIn("Quantifiable ROI Metrics", res["response"])

    def test_interview_prep_query(self):
        res = copilot_assistant.answer_query(
            query="Prepare me for tomorrow's interview",
            resume_context=self.mock_resume
        )
        self.assertTrue(res["success"])
        self.assertIn("STAR Method", res["response"])

if __name__ == "__main__":
    unittest.main()
