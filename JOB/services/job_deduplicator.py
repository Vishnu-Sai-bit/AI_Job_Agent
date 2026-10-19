from typing import Optional
from rapidfuzz import fuzz
from models.job import Job

class JobDeduplicator:
    def find_duplicate(self, candidate_data: dict, existing_jobs: list[Job]) -> Optional[Job]:
        """
        Determines whether the candidate job record is a duplicate of an already stored job.
        Rules:
        1. Exact match on (source_platform, source_job_id)
        2. Exact match on clean apply_url or original_url
        3. High fuzzy match on same company, location, and title similarity >= 92%
        """
        source_platform = candidate_data.get("source_platform", "").lower()
        source_job_id = candidate_data.get("source_job_id", "")
        cand_apply_url = candidate_data.get("apply_url", "").lower()
        cand_orig_url = candidate_data.get("original_url", "").lower()
        cand_company = candidate_data.get("company", "").lower()
        cand_title = candidate_data.get("title", "").lower()
        cand_loc = candidate_data.get("location", "").lower()

        for job in existing_jobs:
            # 1. Exact source platform & job ID
            if job.source_platform.lower() == source_platform and job.source_job_id == source_job_id:
                return job

            # 2. Exact URL match
            if job.apply_url.lower() == cand_apply_url or job.original_url.lower() == cand_orig_url:
                return job

            # 3. Fuzzy company & title matching across platforms
            if job.company.lower() == cand_company and cand_company:
                title_sim = fuzz.ratio(job.title.lower(), cand_title)
                if title_sim >= 92:
                    # Check location alignment
                    if job.location.lower() == cand_loc or "remote" in (job.location + cand_loc).lower():
                        return job

        return None
