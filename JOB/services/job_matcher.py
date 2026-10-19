import re
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models.job import Job
from models.resume import Resume
from models.user import CandidateProfile

class JobMatcher:
    # Component weights without Location:
    # M = 0.40S + 0.25E + 0.15K + 0.10P + 0.10Q
    W_SKILLS = 0.40
    W_EXPERIENCE = 0.25
    W_KEYWORDS = 0.15
    W_PROJECTS = 0.10
    W_QUALIFICATIONS = 0.10

    def compute_match(
        self,
        resume: Resume,
        profile: CandidateProfile,
        job: Job
    ) -> Dict[str, Any]:
        """
        Calculates explainable ATS Job Compatibility Score and breakdown.
        Formula: M = 0.40S + 0.25E + 0.15K + 0.10P + 0.10Q
        (Location & Work Mode fit is treated as an informative eligibility flag, not scored in ATS qualification).
        """
        resume_data = resume.parsed_data or {}
        candidate_skills = [s.lower() for s in (resume_data.get("skills") or profile.skills or [])]
        candidate_years = float(resume_data.get("experience_years") or profile.experience_years or 0.0)
        candidate_projects = resume_data.get("projects") or profile.projects or []
        candidate_education = resume_data.get("education") or profile.education or []
        resume_raw_text = resume.raw_text or ""

        # 1. Skills Alignment (S - 40%)
        s_score, skill_details = self._score_skills(candidate_skills, job)

        # 2. Experience Alignment (E - 25%)
        e_score, exp_details = self._score_experience(candidate_years, job)

        # 3. Keyword Coverage (K - 15%)
        k_score = self._score_keyword_coverage(resume_raw_text, job.description)

        # 4. Project Alignment (P - 10%)
        p_score, proj_details = self._score_projects(candidate_projects, job)

        # 5. Qualification Alignment (Q - 10%)
        q_score, qual_details = self._score_qualifications(candidate_education, job)

        # Advisory Location & Work Mode flags (informational advisory, 0% ATS weight)
        _, loc_flags = self._score_location_and_work_mode(profile, job)

        # Weighted ATS compatibility calculation
        total_score = round(
            self.W_SKILLS * s_score +
            self.W_EXPERIENCE * e_score +
            self.W_KEYWORDS * k_score +
            self.W_PROJECTS * p_score +
            self.W_QUALIFICATIONS * q_score,
            2
        )
        total_score = max(0.0, min(100.0, total_score))

        # Generate transparent, explainable narrative
        explanation, eligibility_flags = self._generate_explanation(
            total_score,
            skill_details,
            exp_details,
            loc_flags,
            job
        )

        return {
            "match_score": total_score,
            "score_breakdown": {
                "skills": round(s_score, 1),
                "experience": round(e_score, 1),
                "keyword_coverage": round(k_score, 1),
                "projects": round(p_score, 1),
                "qualifications": round(q_score, 1)
            },
            "skill_match_details": skill_details,
            "match_explanation": explanation,
            "eligibility_flags": eligibility_flags
        }

    def _score_skills(self, candidate_skills: List[str], job: Job) -> Tuple[float, Dict[str, Any]]:
        req_skills = [s.lower() for s in (job.required_skills or [])]
        pref_skills = [s.lower() for s in (job.preferred_skills or [])]

        matched_req = [s.title() for s in req_skills if any(cs in s or s in cs for cs in candidate_skills)]
        missing_req = [s.title() for s in req_skills if s.title() not in matched_req]

        matched_pref = [s.title() for s in pref_skills if any(cs in s or s in cs for cs in candidate_skills)]
        missing_pref = [s.title() for s in pref_skills if s.title() not in matched_pref]

        # If job has no parsed required skills, check matching candidate skills in description
        if not req_skills:
            job_desc_lower = job.description.lower()
            matched_desc = [s.title() for s in candidate_skills if s in job_desc_lower]
            s_score = min(100.0, max(50.0, len(matched_desc) * 12.0))
            return s_score, {
                "matched_required": matched_desc,
                "missing_required": [],
                "matched_preferred": [],
                "missing_preferred": []
            }

        # Weight required skills at 80% of skills score, preferred at 20%
        req_ratio = len(matched_req) / max(len(req_skills), 1)
        pref_ratio = len(matched_pref) / max(len(pref_skills), 1) if pref_skills else 1.0

        score = (req_ratio * 80.0) + (pref_ratio * 20.0)
        return min(100.0, max(0.0, score)), {
            "matched_required": matched_req,
            "missing_required": missing_req,
            "matched_preferred": matched_pref,
            "missing_preferred": missing_pref
        }

    def _score_experience(self, cand_years: float, job: Job) -> Tuple[float, str]:
        exp_lvl = (job.experience_level or "mid").lower()
        title_lower = job.title.lower()

        # Parse target years if explicitly stated in description e.g. "5+ years"
        years_match = re.search(r"(\d+)\+?\s*years?(?:\s+of)?\s+experience", job.description, re.IGNORECASE)
        target_years = int(years_match.group(1)) if years_match else None

        if target_years is None:
            if "entry" in exp_lvl or "fresher" in title_lower or "intern" in title_lower:
                target_years = 1
            elif "senior" in exp_lvl or "sr." in title_lower:
                target_years = 5
            elif "lead" in exp_lvl or "principal" in title_lower or "architect" in title_lower:
                target_years = 8
            else:
                target_years = 3

        if cand_years >= target_years:
            score = 100.0
            detail = f"Meets or exceeds target experience ({cand_years:.1f} yrs vs {target_years} yrs required)."
        else:
            ratio = cand_years / max(target_years, 1)
            score = max(40.0, ratio * 90.0)
            detail = f"Has {cand_years:.1f} years experience; position targets around {target_years} years."

        return score, detail

    def _score_keyword_coverage(self, resume_text: str, job_desc: str) -> float:
        if not resume_text or not job_desc:
            return 50.0
        try:
            vectorizer = TfidfVectorizer(stop_words="english", max_features=100)
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_desc])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Rescale cosine similarity typically ranging 0.1 to 0.7 into 0 to 100
            score = min(100.0, max(30.0, sim * 150.0))
            return score
        except Exception:
            return 60.0

    def _score_projects(self, projects: List[Any], job: Job) -> Tuple[float, str]:
        if not projects:
            return 50.0, "No projects detailed on resume."
        
        job_terms = set(job.title.lower().split() + [s.lower() for s in (job.required_skills or [])])
        match_count = 0
        for p in projects:
            desc = (p.get("description", "") + " " + p.get("title", "")).lower() if isinstance(p, dict) else str(p).lower()
            if any(term in desc for term in job_terms if len(term) > 2):
                match_count += 1

        score = min(100.0, 60.0 + (match_count * 15.0))
        return score, f"{match_count} projects show relevant domain or technical overlap."

    def _score_location_and_work_mode(self, profile: CandidateProfile, job: Job) -> Tuple[float, List[str]]:
        flags = []
        user_modes = [m.lower() for m in (profile.work_modes or ["remote", "hybrid", "on-site"])]
        job_mode = (job.work_mode or "on-site").lower()

        if job_mode == "remote":
            if "remote" in user_modes:
                return 100.0, flags
            return 80.0, flags

        # Job is on-site or hybrid
        cand_loc = (profile.location or "").lower()
        pref_countries = [c.lower() for c in (profile.preferred_countries or [])]
        pref_cities = [c.lower() for c in (profile.preferred_cities or [])]
        job_loc = (job.location or "").lower()

        is_match = False
        if cand_loc and (cand_loc in job_loc or job_loc in cand_loc):
            is_match = True
        elif any(c in job_loc for c in pref_countries if c) or any(c in job_loc for c in pref_cities if c):
            is_match = True

        if is_match:
            return 100.0, flags
        else:
            flags.append(f"Requires {job_mode} presence in {job.location or 'employer office'}.")
            return 50.0, flags

    def _score_qualifications(self, education: List[Any], job: Job) -> Tuple[float, str]:
        if not education:
            return 75.0, "Degree not explicitly stated."
        return 90.0, "Educational background aligns with standard qualifications."

    def _generate_explanation(
        self,
        total_score: float,
        skill_details: Dict[str, Any],
        exp_details: str,
        loc_flags: List[str],
        job: Job
    ) -> Tuple[str, List[str]]:
        matched = skill_details.get("matched_required", [])
        missing = skill_details.get("missing_required", [])
        
        tier = "Strong match" if total_score >= 80 else ("Moderate match" if total_score >= 60 else "Potential growth match")
        
        parts = [f"{tier} ({total_score:.1f}% compatibility)."]
        if matched:
            parts.append(f"Skills matched: {', '.join(matched[:5])}.")
        if missing:
            parts.append(f"Missing evidence in resume for: {', '.join(missing[:4])}.")
        parts.append(exp_details)

        explanation = " ".join(parts)
        return explanation, loc_flags
