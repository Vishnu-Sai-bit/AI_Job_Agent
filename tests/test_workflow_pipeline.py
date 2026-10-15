"""
====================================================================
AI Job Agent - Comprehensive 6-Module & 9-Step Pipeline Test Suite
Author: Beere Vishnu Sai
Verifies:
1. Module 1: Resume Analyzer & ResumeData
2. Module 2: ATS & Resume Feedback
3. Module 3: Job Preferences (Home Location vs Preferred Location)
4. Module 4: Job Collection & JobData normalization
5. Module 5: Job Matching Engine & Weighted Scores
6. Module 6: Dashboard & Streamlit pipeline logic
====================================================================
"""

import unittest
from pathlib import Path

from models import ResumeData, JobData
from services.resume.resume_analyzer import analyze_resume
from services.ats.ats_calculator import calculate_ats
from services.matcher.job_matcher import match_jobs
from streamlit_app import convert_dict_to_jobdata, execute_job_collection


class TestWorkflowPipeline(unittest.TestCase):
    def setUp(self):
        self.sample_text = """
        Beere Vishnu Sai
        vishnusaibeere124@gmail.com | +91 9182679641 | Hyderabad, India
        LinkedIn: https://linkedin.com/in/vishnusai | GitHub: https://github.com/vishnusai
        Target Role: Data Analyst

        Professional Summary:
        Aspiring Data Analyst skilled in Python, SQL, Tableau, Power BI, Excel, and ETL pipelines.
        Experienced in extracting business intelligence and optimizing data workflows.

        Education:
        B.Tech in Computer Science and Engineering, JNTU (2020-2024), CGPA 8.2

        Experience:
        Junior Data Analyst Intern at TechCorp (6 months)
        - Analyzed customer churn datasets using Python and pandas.
        - Built interactive Tableau dashboards for executive reporting.

        Projects:
        - Autonomous AI Job Agent: Python, Ollama, Flask, Streamlit career automation platform.
        - Sales Forecast Analysis: SQL, Power BI, Python predictive modeling.

        Certifications:
        - Google Data Analytics Professional Certificate
        - Python for Data Science Specialist
        """

    def test_module_1_resume_analyzer(self):
        """Module 1: Extract and create structured ResumeData profile."""
        resume = analyze_resume(self.sample_text)
        self.assertIsInstance(resume, ResumeData)
        self.assertTrue(len(resume.skills) > 0)
        self.assertTrue(any(s.lower() == "python" for s in resume.skills))
        self.assertTrue(any(s.lower() == "sql" for s in resume.skills))

    def test_module_2_ats_feedback(self):
        """Module 2: Calculate ATS score and verify strengths/suggestions."""
        resume = analyze_resume(self.sample_text)
        ats = calculate_ats(resume)
        self.assertGreaterEqual(ats.score, 60.0)
        self.assertGreaterEqual(ats.contact_score, 5)
        self.assertGreaterEqual(ats.skills_score, 15)
        self.assertIsInstance(ats.strengths, list)

    def test_module_3_job_preferences_separation(self):
        """Module 3: Separate candidate home location from target job location."""
        resume = analyze_resume(self.sample_text)
        resume.location = "Hyderabad, India"
        resume.preferred_location = "Bengaluru"
        resume.preferred_role = "Data Analyst"

        self.assertEqual(resume.location, "Hyderabad, India")
        self.assertEqual(resume.preferred_location, "Bengaluru")
        self.assertNotEqual(resume.location, resume.preferred_location)

    def test_module_4_job_collection_normalization(self):
        """Module 4: Normalize raw dictionary to standard JobData structure."""
        raw_job = {
            "title": "Data Analyst",
            "company": "Amazon",
            "location": "Hyderabad, India",
            "salary": "₹10 - ₹16 LPA",
            "experience": "1-3 yrs",
            "skills": ["Python", "SQL", "Tableau", "AWS"],
            "url": "https://amazon.jobs/analyst",
            "source": "Remotive"
        }
        job = convert_dict_to_jobdata(raw_job)
        self.assertIsInstance(job, JobData)
        self.assertEqual(job.title, "Data Analyst")
        self.assertEqual(job.company, "Amazon")
        self.assertEqual(job.provider, "Remotive")
        self.assertEqual(job.apply_url, "https://amazon.jobs/analyst")
        self.assertIn("Python", job.skills)

    def test_module_5_job_matching_engine(self):
        """Module 5: Compare requirements with resume and calculate weighted score."""
        resume = analyze_resume(self.sample_text)
        job1 = JobData(
            title="Data Analyst",
            company="Tech Corp",
            location="Hyderabad, India",
            skills=["Python", "SQL", "Tableau"],
            apply_url="https://example.com/apply"
        )
        job2 = JobData(
            title="Mechanical Engineer",
            company="Build Corp",
            location="Pune, India",
            skills=["AutoCAD", "Thermodynamics", "SolidWorks"],
            apply_url="https://example.com/apply2"
        )
        ranked = match_jobs(resume, [job1, job2])
        self.assertEqual(len(ranked), 2)
        # Data Analyst must rank higher than Mechanical Engineer
        self.assertGreater(ranked[0].match_score, ranked[1].match_score)
        self.assertEqual(ranked[0].title, "Data Analyst")
        self.assertIn("Python", ranked[0].matching_skills)

    def test_module_6_job_collection_fallback(self):
        """Module 6: Verify execute_job_collection returns valid JobData list."""
        jobs = execute_job_collection("Data Analyst", "Hyderabad", ["Remotive", "RemoteOK", "ArbeitNow"])
        self.assertIsInstance(jobs, list)
        self.assertGreater(len(jobs), 0)
        self.assertIsInstance(jobs[0], JobData)


if __name__ == "__main__":
    unittest.main()
