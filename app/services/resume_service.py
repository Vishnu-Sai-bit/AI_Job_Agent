"""
==========================================================
AI Job Copilot - Resume Service
==========================================================
"""

from pathlib import Path
from typing import Dict, Any
from services.resume.resume_parser import extract_resume_text
from services.resume.resume_analyzer import analyze_resume
from services.ats.ats_calculator import calculate_ats

class ResumeService:
    @staticmethod
    def process_resume_file(file_path: Path) -> Dict[str, Any]:
        raw_text = extract_resume_text(file_path)
        resume_data = analyze_resume(raw_text)
        ats_report = calculate_ats(resume_data)
        return {
            "name": resume_data.name,
            "email": resume_data.email,
            "phone": resume_data.phone,
            "skills": resume_data.skills,
            "experience_years": resume_data.experience_years,
            "education": resume_data.education,
            "projects": resume_data.projects,
            "certifications": resume_data.certifications,
            "ats_score": round(ats_report.score, 1),
            "ats_breakdown": {
                "contact_score": ats_report.contact_score,
                "skills_score": ats_report.skills_score,
                "experience_score": ats_report.experience_score,
                "education_score": ats_report.education_score,
                "projects_score": ats_report.projects_score,
                "certifications_score": ats_report.certifications_score,
            },
            "strengths": ats_report.strengths,
            "weaknesses": ats_report.weaknesses,
            "suggestions": ats_report.suggestions,
            "career_summary": resume_data.career_summary
        }

resume_service = ResumeService()
