"""
==========================================================
AI JobAgent - ATS Scorer & Compatibility Engine
Implements the two distinct scoring tiers defined in the blueprint:
1. Resume Quality Score: Completeness, readability, presentation (0-100)
2. Job Compatibility Score: M = 0.35S + 0.20E + 0.15K + 0.10P + 0.10L + 0.10Q
   - S: Required and relevant skill alignment (0-100)
   - E: Relevant experience alignment (0-100)
   - K: Job-description keyword coverage (0-100)
   - P: Project and evidence alignment (0-100)
   - L: Location and work-mode alignment (0-100)
   - Q: Qualification alignment (0-100)
==========================================================
"""

import re
from typing import Dict, Any, List, Optional, Tuple


def calculate_resume_quality_score(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate how complete, readable, and well-presented the candidate's resume is.
    Does NOT depend on a specific job opening.
    Weights: Contact 10%, Skills 30%, Education 15%, Experience 20%, Projects 15%, Certifications 10%.
    """
    skills = resume_data.get("skills") or []
    experience_years = float(resume_data.get("experience_years") or 0.0)
    education = resume_data.get("education") or []
    projects = resume_data.get("projects") or []
    certifications = resume_data.get("certifications") or []

    # 1. Contact (10 pts)
    contact_pts = 0.0
    if resume_data.get("candidate_name") or resume_data.get("name"):
        contact_pts += 2.0
    if resume_data.get("email"):
        contact_pts += 3.0
    if resume_data.get("phone"):
        contact_pts += 3.0
    if resume_data.get("linkedin"):
        contact_pts += 1.0
    if resume_data.get("github") or resume_data.get("portfolio"):
        contact_pts += 1.0
    contact_score = min(10.0, contact_pts)

    # 2. Skills (30 pts)
    total_skills = len(skills)
    if total_skills >= 10:
        skills_score = 30.0
    elif total_skills >= 7:
        skills_score = 25.0
    elif total_skills >= 4:
        skills_score = 18.0
    elif total_skills >= 1:
        skills_score = 10.0
    else:
        skills_score = 0.0

    # 3. Experience (20 pts)
    if experience_years >= 3.0:
        exp_score = 20.0
    elif experience_years >= 1.0:
        exp_score = 16.0
    elif experience_years > 0.0:
        exp_score = 12.0
    else:
        exp_score = 8.0

    # 4. Education (15 pts)
    edu_score = 15.0 if education else 8.0

    # 5. Projects (15 pts)
    proj_len = len(projects)
    if proj_len >= 3:
        proj_score = 15.0
    elif proj_len >= 1:
        proj_score = 12.0
    else:
        proj_score = 6.0

    # 6. Certifications (10 pts)
    cert_score = 10.0 if certifications else 5.0

    overall = round(contact_score + skills_score + exp_score + edu_score + proj_score + cert_score, 1)

    return {
        "overall_score": overall,
        "contact_score": contact_score,
        "skills_score": skills_score,
        "experience_score": exp_score,
        "education_score": edu_score,
        "projects_score": proj_score,
        "certifications_score": cert_score,
        "suggestions": [
            "Quantify project achievements with measurable metrics (e.g. latency reduced by 30%, data pipeline scaled to 5M records).",
            "Ensure certifications section highlights verified cloud and domain accreditations.",
            "Maintain clean bullet points adhering to standard industry ATS formatting guidelines."
        ]
    }


def calculate_job_compatibility_score(
    candidate: Dict[str, Any],
    job: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate explainable job-specific compatibility score using the blueprint formula:
    M = 0.35*S + 0.20*E + 0.15*K + 0.10*P + 0.10*L + 0.10*Q
    """
    cand_skills_raw = candidate.get("skills") or []
    cand_skills = {str(s).strip().lower() for s in cand_skills_raw if str(s).strip()}
    cand_exp = float(candidate.get("experience_years") or 0.0)
    cand_projects = candidate.get("projects") or []
    cand_edu = candidate.get("education") or []
    cand_loc = (candidate.get("preferred_location") or candidate.get("location") or "India").lower().strip()

    job_title = (job.get("title") or job.get("job_title") or "").strip()
    job_desc = (job.get("description") or "").strip()
    job_loc = (job.get("location") or "India").strip()
    job_exp_str = (job.get("experience") or "1-3 yrs").strip()
    raw_job_skills = job.get("skills") or []

    if isinstance(raw_job_skills, list):
        job_skills = [str(s).strip() for s in raw_job_skills if str(s).strip()]
    else:
        job_skills = [s.strip() for s in str(raw_job_skills).split(",") if s.strip()]

    # S: Required & relevant skill alignment (0 - 100, weight 0.35)
    matched_skills = []
    missing_skills = []
    for js in job_skills:
        js_low = js.lower()
        if any(js_low == cs or js_low in cs or cs in js_low for cs in cand_skills):
            matched_skills.append(js)
        else:
            missing_skills.append(js)

    if job_skills:
        S = round((len(matched_skills) / len(job_skills)) * 100.0, 1)
    else:
        S = 75.0 if cand_skills else 50.0

    # E: Relevant experience alignment (0 - 100, weight 0.20)
    exp_nums = re.findall(r"\d+", job_exp_str)
    if exp_nums:
        min_exp = float(exp_nums[0])
        max_exp = float(exp_nums[1]) if len(exp_nums) > 1 else (min_exp + 3.0)
        if min_exp <= cand_exp <= max_exp:
            E = 100.0
            exp_note = f"Directly aligned ({job_exp_str} fits your {cand_exp:g} yrs)"
        elif cand_exp >= max_exp:
            E = 90.0
            exp_note = f"Qualified ({cand_exp:g} yrs qualifies for {job_exp_str})"
        elif cand_exp >= max_exp - 1.0:
            E = 75.0
            exp_note = f"Target fit for {job_exp_str}"
        else:
            E = max(40.0, round(50.0 - (min_exp - cand_exp) * 10.0, 1))
            exp_note = f"Requires {job_exp_str}"
    else:
        E = 85.0
        exp_note = "General experience alignment"

    # K: Job description keyword coverage (0 - 100, weight 0.15)
    text_corpus = (job_title + " " + job_desc).lower()
    important_terms = [
        "python", "sql", "api", "database", "git", "cloud", "agile", "testing",
        "data", "docker", "pipeline", "analytics", "architecture", "collaboration"
    ]
    present_terms = [t for t in important_terms if t in text_corpus]
    cand_text = " ".join(cand_skills) + " " + str(candidate.get("career_summary") or "")
    matched_keywords = [t for t in present_terms if t in cand_text.lower()]
    if present_terms:
        K = round((len(matched_keywords) / len(present_terms)) * 100.0, 1)
    else:
        K = 80.0

    # P: Project and evidence alignment (0 - 100, weight 0.10)
    if len(cand_projects) >= 3:
        P = 95.0
    elif len(cand_projects) >= 1:
        P = 80.0
    elif cand_skills:
        P = 70.0
    else:
        P = 50.0

    # L: Location & work-mode preference alignment (0 - 100, weight 0.10)
    j_loc_low = job_loc.lower()
    if "remote" in j_loc_low or "anywhere" in j_loc_low:
        L = 100.0
        loc_note = "Worldwide / Remote Flexibility"
    elif cand_loc and (cand_loc in j_loc_low or j_loc_low in cand_loc):
        L = 100.0
        loc_note = f"Exact match for {job_loc}"
    elif any(c in j_loc_low for c in ["hyderabad", "bangalore", "bengaluru", "pune", "mumbai", "noida", "delhi"]):
        L = 85.0
        loc_note = f"Metropolitan hub ({job_loc})"
    else:
        L = 70.0
        loc_note = job_loc

    # Q: Qualification alignment (0 - 100, weight 0.10)
    if cand_edu:
        Q = 90.0
    elif cand_exp >= 1.0 or cand_skills:
        Q = 80.0
    else:
        Q = 65.0

    # Calculate weighted compatibility score:
    # M = 0.35S + 0.20E + 0.15K + 0.10P + 0.10L + 0.10Q
    M = round(0.35 * S + 0.20 * E + 0.15 * K + 0.10 * P + 0.10 * L + 0.10 * Q, 1)
    M = min(98.0, max(30.0, M))

    if M >= 80.0:
        match_label = "Strong match"
    elif M >= 65.0:
        match_label = "Moderate match"
    else:
        match_label = "Potential fit"

    return {
        "match_score": M,
        "match_label": match_label,
        "formula": "M = 0.35S + 0.20E + 0.15K + 0.10P + 0.10L + 0.10Q",
        "matching_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords": matched_keywords,
        "experience_note": exp_note,
        "location_note": loc_note,
        "components": {
            "S": {"score": S, "weight": 0.35, "weighted": round(0.35 * S, 2), "label": "Skills Alignment"},
            "E": {"score": E, "weight": 0.20, "weighted": round(0.20 * E, 2), "label": "Experience Alignment"},
            "K": {"score": K, "weight": 0.15, "weighted": round(0.15 * K, 2), "label": "Keyword Coverage"},
            "P": {"score": P, "weight": 0.10, "weighted": round(0.10 * P, 2), "label": "Project & Evidence"},
            "L": {"score": L, "weight": 0.10, "weighted": round(0.10 * L, 2), "label": "Location & Work Mode"},
            "Q": {"score": Q, "weight": 0.10, "weighted": round(0.10 * Q, 2), "label": "Qualifications"}
        }
    }
