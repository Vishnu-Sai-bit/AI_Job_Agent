"""
==========================================================
AI JobAgent - Refresh Jobs Orchestration Service
Coordinates multi-source job collection, normalization,
deduplication, verification, resume matching, and SQLite persistence.
==========================================================
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collectors import ALL_COLLECTORS
from services.job_normalizer import normalize_job_dict
from services.deduplication import deduplicate_jobs
from services.job_verifier import verify_job_listing
from services.job_matcher import match_and_rank_jobs
from database.db import save_job, get_all_jobs
from utils import info, warning


class JobRefreshService:
    """Orchestrates end-to-end multi-platform job aggregation and verification."""

    def __init__(self, collectors=None):
        self.collectors = [cls() for cls in (collectors or ALL_COLLECTORS)]

    def run_refresh(
        self,
        query: str = "Data Analyst",
        location: str = "India",
        candidate_skills: Optional[List[str]] = None,
        limit_per_source: int = 15,
        persist_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Executes a complete refresh across all configured ATS platforms and job sources.
        """
        raw_collected: List[Dict[str, Any]] = []
        source_counts: Dict[str, int] = {}

        # Step 1: Collect from all sources
        for col in self.collectors:
            try:
                col_name = getattr(col, "name", col.__class__.__name__)
                items = col.fetch_jobs(query=query, location=location, limit=limit_per_source)
                raw_collected.extend(items)
                source_counts[col_name] = len(items)
                info(f"[{col_name}] Collected {len(items)} listings.")
            except Exception as e:
                warning(f"Error collecting from {col}: {e}")

        # Step 2: Normalize to 11 fields (with zero salary)
        normalized_jobs = [normalize_job_dict(item) for item in raw_collected]

        # Step 3: Multi-factor deduplication
        unique_jobs = deduplicate_jobs(normalized_jobs)

        # Step 4: Verification (syntax, non-aggregator direct check, active status)
        verified_jobs = [verify_job_listing(j) for j in unique_jobs]

        # Step 5: Resume matching & ranking
        ranked_jobs = match_and_rank_jobs(
            verified_jobs,
            candidate_skills=candidate_skills,
            candidate_role=query
        )

        # Step 6: Persist to database
        saved_count = 0
        if persist_to_db:
            for job in ranked_jobs:
                try:
                    save_job(job)
                    saved_count += 1
                except Exception as e:
                    warning(f"Error saving job #{job.get('job_id')} to DB: {e}")

        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "location": location,
            "total_raw": len(raw_collected),
            "total_unique": len(unique_jobs),
            "total_verified": len(verified_jobs),
            "saved_count": saved_count,
            "sources": source_counts,
            "jobs": ranked_jobs
        }


def refresh_all_jobs(
    query: str = "Data Analyst",
    location: str = "India",
    candidate_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Functional convenience entrypoint for triggering full pipeline refresh."""
    service = JobRefreshService()
    return service.run_refresh(query=query, location=location, candidate_skills=candidate_skills)
