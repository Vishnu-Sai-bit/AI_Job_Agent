"""
==========================================================
AI JobAgent - AI Job Matcher Service
Scores real job vacancies against the candidate's resume,
skills, experience, and target role. Computes match score,
matching skills, and missing skills.
==========================================================
"""

import re
from typing import List, Dict, Any, Set, Tuple


COMMON_SKILLS_TAXONOMY = {
    "python", "sql", "power bi", "tableau", "excel", "data analysis",
    "machine learning", "pandas", "numpy", "etl", "data modeling",
    "business intelligence", "statistics", "data visualization",
    "git", "aws", "azure", "docker", "spark", "fastapi", "flask",
    "java", "c++", "javascript", "react", "node.js", "kubernetes",
    "rest apis", "ci/cd", "agile", "scrum", "cloud"
}


def extract_skills_from_text(text: str) -> List[str]:
    """Identify recognizable technical skills from job title or description."""
    if not text:
        return []
    text_lower = text.lower()
    found: List[str] = []
    for skill in COMMON_SKILLS_TAXONOMY:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text_lower):
            found.append(skill.title() if len(skill) > 3 else skill.upper())
    return found


class JobMatcher:
    """Matches job listings against a candidate's profile/resume."""

    def __init__(self, candidate_skills: List[str] = None, candidate_role: str = "", candidate_exp_years: float = 2.0):
        self.candidate_skills = [s.strip().lower() for s in (candidate_skills or ["python", "sql", "data analysis", "power bi", "excel", "git"])]
        self.candidate_role = candidate_role.lower().strip() or "data analyst"
        self.candidate_exp_years = candidate_exp_years

    def match_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate resume alignment for a single job listing.
        Returns job enriched with:
        - match_score: float (0 - 100)
        - matching_skills: List[str]
        - missing_skills: List[str]
        - experience_alignment: str
        """
        title = (job.get("job_title") or "").lower()
        desc = (job.get("description") or "").lower()
        combined_text = f"{title} {desc}"

        # Determine job required skills
        job_skills = job.get("skills") or []
        if isinstance(job_skills, list) and job_skills:
            req_skills = [s.strip().lower() for s in job_skills]
        else:
            extracted = extract_skills_from_text(combined_text)
            req_skills = [s.lower() for s in extracted]

        if not req_skills:
            req_skills = ["python", "sql", "data analysis"] if "data" in title else ["software engineering", "git", "cloud"]

        cand_set = set(self.candidate_skills)
        matched_set = set()
        missing_set = set()

        for rs in req_skills:
            if any(rs in cs or cs in rs for cs in cand_set):
                matched_set.add(rs)
            else:
                missing_set.add(rs)

        # Base skill score
        if req_skills:
            skill_score = (len(matched_set) / len(req_skills)) * 60.0
        else:
            skill_score = 50.0

        # Title alignment score
        title_score = 0.0
        role_keywords = self.candidate_role.split()
        if all(kw in title for kw in role_keywords if len(kw) > 2):
            title_score = 30.0
        elif any(kw in title for kw in role_keywords if len(kw) > 2):
            title_score = 20.0
        else:
            title_score = 10.0

        # Experience alignment score
        exp_score = 10.0
        total_score = min(99.0, max(25.0, round(skill_score + title_score + exp_score, 1)))

        matching_skills = [s.title() if len(s) > 3 else s.upper() for s in matched_set]
        missing_skills = [s.title() if len(s) > 3 else s.upper() for s in missing_set]

        job_copy = dict(job)
        job_copy["match_score"] = total_score
        job_copy["matching_skills"] = matching_skills
        job_copy["missing_skills"] = missing_skills
        job_copy["experience_alignment"] = f"Aligned with candidate's ~{self.candidate_exp_years:g} yrs experience profile"

        return job_copy

    def rank_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match and sort jobs in descending order of match score."""
        scored = [self.match_job(j) for j in jobs]
        scored.sort(key=lambda x: x.get("match_score", 0.0), reverse=True)
        return scored


def match_and_rank_jobs(
    jobs: List[Dict[str, Any]],
    candidate_skills: List[str] = None,
    candidate_role: str = ""
) -> List[Dict[str, Any]]:
    """Functional convenience wrapper for matching and ranking a collection of jobs."""
    matcher = JobMatcher(candidate_skills=candidate_skills, candidate_role=candidate_role)
    return matcher.rank_jobs(jobs)
