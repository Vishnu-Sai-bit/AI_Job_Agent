import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import Dict, Any, List
from collectors.base_collector import RawJobRecord
from services.resume_parser import COMMON_SKILLS

class JobNormalizer:
    TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}

    def normalize(self, raw: RawJobRecord) -> Dict[str, Any]:
        """
        Transforms RawJobRecord into normalized dictionary suitable for the Job model.
        """
        title = self._clean_title(raw.title)
        work_mode = self._detect_work_mode(raw.title, raw.location, raw.description, raw.work_mode)
        country, city = self._parse_location(raw.location)
        emp_type = self._normalize_employment_type(raw.employment_type)
        exp_level = self._detect_experience_level(raw.title, raw.description, raw.experience_level)
        
        req_skills, pref_skills = self._extract_job_skills(raw.description, raw.required_skills)
        clean_orig_url = self._clean_url(raw.original_url)
        clean_apply_url = self._clean_url(raw.apply_url)

        return {
            "source_platform": raw.source_platform.lower(),
            "source_company_key": raw.source_company_key.lower(),
            "source_job_id": str(raw.source_job_id).strip(),
            "title": title,
            "company": raw.company.strip(),
            "department": raw.department.strip(),
            "location": raw.location.strip() or ("Remote" if work_mode == "remote" else "Unspecified"),
            "country": country,
            "city": city,
            "work_mode": work_mode,
            "employment_type": emp_type,
            "experience_level": exp_level,
            "salary_min": raw.salary_min,
            "salary_max": raw.salary_max,
            "currency": raw.currency,
            "description": raw.description.strip(),
            "raw_description": raw.raw_description,
            "required_skills": req_skills,
            "preferred_skills": pref_skills,
            "original_url": clean_orig_url,
            "apply_url": clean_apply_url,
            "canonical_url": raw.canonical_url or clean_orig_url,
            "published_at": raw.published_at,
            "source_metadata": raw.source_metadata
        }

    def _clean_title(self, title: str) -> str:
        cleaned = re.sub(r"\((m/w/d|m/f/d|w/m/d)\)", "", title, flags=re.IGNORECASE)
        cleaned = re.sub(r"\[(remote|hybrid)\]", "", cleaned, flags=re.IGNORECASE)
        return " ".join(cleaned.split()).strip()

    def _detect_work_mode(self, title: str, location: str, desc: str, fallback: str) -> str:
        combined = f"{title} {location} {desc[:500]}".lower()
        if "remote" in combined or "anywhere" in combined or "work from home" in combined:
            return "remote"
        if "hybrid" in combined:
            return "hybrid"
        if fallback in ("remote", "hybrid", "on-site"):
            return fallback
        return "on-site"

    def _parse_location(self, location_str: str) -> (str, str):
        if not location_str:
            return "", ""
        parts = [p.strip() for p in location_str.split(",") if p.strip()]
        if len(parts) >= 2:
            return parts[-1], parts[0]
        elif len(parts) == 1:
            return parts[0], ""
        return "", ""

    def _normalize_employment_type(self, emp_type: str) -> str:
        lowered = emp_type.lower()
        if "part" in lowered:
            return "part-time"
        if "contract" in lowered or "freelance" in lowered:
            return "contract"
        if "intern" in lowered:
            return "internship"
        return "full-time"

    def _detect_experience_level(self, title: str, desc: str, fallback: str) -> str:
        combined = f"{title} {desc[:400]}".lower()
        if any(w in combined for w in ["lead", "principal", "architect", "staff", "director", "head of"]):
            return "lead"
        if any(w in combined for w in ["senior", "sr.", "sr "]):
            return "senior"
        if any(w in combined for w in ["entry", "junior", "jr.", "jr ", "fresher", "graduate", "intern"]):
            return "entry"
        if fallback in ("entry", "mid", "senior", "lead"):
            return fallback
        return "mid"

    def _extract_job_skills(self, desc: str, explicit_skills: List[str]) -> (List[str], List[str]):
        skills_found = set(explicit_skills)
        lowered = desc.lower()

        for skill in COMMON_SKILLS:
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
            if re.search(pattern, lowered):
                skills_found.add(self._canonicalize_skill(skill))

        req_skills = []
        pref_skills = []

        pref_match = re.search(r"\b(preferred|nice to have|plus|bonus|desirable|optional)\b", lowered)
        if pref_match:
            split_idx = pref_match.start()
            req_text = lowered[:split_idx]
            pref_text = lowered[split_idx:]
            for s in skills_found:
                s_low = s.lower()
                pattern = r"(?<!\w)" + re.escape(s_low) + r"(?!\w)"
                if re.search(pattern, req_text):
                    req_skills.append(s)
                elif re.search(pattern, pref_text):
                    pref_skills.append(s)
                else:
                    req_skills.append(s)
        else:
            req_skills = list(skills_found)

        return sorted(list(set(req_skills)))[:15], sorted(list(set(pref_skills)))[:10]

    def _canonicalize_skill(self, skill: str) -> str:
        mapping = {
            "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
            "react": "React", "react.js": "React", "vue": "Vue.js", "vue.js": "Vue.js",
            "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
            "node.js": "Node.js", "nodejs": "Node.js", "sql": "SQL",
            "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mongodb": "MongoDB",
            "docker": "Docker", "kubernetes": "Kubernetes", "aws": "AWS",
            "gcp": "GCP", "azure": "Azure", "ci/cd": "CI/CD", "html": "HTML",
            "css": "CSS", "rest": "REST APIs", "rest api": "REST APIs",
            "restful api": "REST APIs", "graphql": "GraphQL", "git": "Git"
        }
        return mapping.get(skill.lower(), skill.title())

    def _clean_url(self, url: str) -> str:
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            query_tuples = parse_qsl(parsed.query, keep_blank_values=True)
            filtered_tuples = [(k, v) for k, v in query_tuples if k.lower() not in self.TRACKING_PARAMS]
            new_query = urlencode(filtered_tuples)
            cleaned = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
            return cleaned
        except Exception:
            return url
