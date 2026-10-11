"""
==========================================================
Job Sources - Schema Normalizer
==========================================================
"""

from typing import Dict, Any

def normalize_job_dict(raw_job: Dict[str, Any], default_source: str = "Aggregator") -> Dict[str, Any]:
    return {
        "id": raw_job.get("id") or str(raw_job.get("slug", "")),
        "title": (raw_job.get("title") or raw_job.get("position", "")).strip(),
        "company": (raw_job.get("company") or raw_job.get("company_name", "")).strip(),
        "location": (raw_job.get("location") or raw_job.get("candidate_required_location", "Remote")).strip(),
        "salary": raw_job.get("salary") or "Competitive",
        "source": raw_job.get("source", default_source),
        "url": raw_job.get("url") or "#",
        "description": raw_job.get("description") or "",
        "skills": raw_job.get("skills") or raw_job.get("tags") or []
    }
