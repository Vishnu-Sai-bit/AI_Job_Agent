"""
==========================================================
AI JobAgent - Free Public ATS Direct Feeder
Queries official free public ATS APIs (Greenhouse, Lever, Ashby)
Directly yields authentic employer jobs with exact job & apply URLs.
No intermediate aggregators (Adzuna, LinkedIn, Indeed) involved.
==========================================================
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from services.job_links.company_registry import COMPANY_ATS_REGISTRY
from services.job_links.adapters.greenhouse import GreenhouseAdapter
from services.job_links.adapters.lever import LeverAdapter
from services.job_links.adapters.ashby import AshbyAdapter

def fetch_direct_ats_jobs(
    role_filter: str = "",
    max_per_provider: int = 15,
    max_total: int = 40
) -> List[Dict[str, Any]]:
    """
    Query official public ATS feeds directly across verified company boards.
    Returns normalized job records with exact official_job_url and apply_url.
    """
    collected: List[Dict[str, Any]] = []
    keywords = [k.lower().strip() for k in role_filter.split() if len(k) > 2] if role_filter else []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}

        # 1. Greenhouse boards
        for comp in COMPANY_ATS_REGISTRY.get("greenhouse", [])[:6]:
            futures[executor.submit(GreenhouseAdapter.fetch_jobs, comp["token"], comp["name"])] = comp["name"]

        # 2. Lever sites
        for comp in COMPANY_ATS_REGISTRY.get("lever", [])[:5]:
            futures[executor.submit(LeverAdapter.fetch_jobs, comp["site"], comp["name"])] = comp["name"]

        # 3. Ashby boards
        for comp in COMPANY_ATS_REGISTRY.get("ashby", [])[:5]:
            futures[executor.submit(AshbyAdapter.fetch_jobs, comp["board"], comp["name"])] = comp["name"]

        for future in as_completed(futures):
            comp_name = futures[future]
            try:
                jobs = future.result()
                if not jobs:
                    continue
                for j in jobs:
                    title = (j.get("job_title") or j.get("title") or "").lower()
                    desc = (j.get("description") or "").lower()
                    
                    # If role keyword specified, check relevance
                    if keywords:
                        if not any(k in title or k in desc for k in keywords):
                            continue

                    collected.append(j)
                    if len(collected) >= max_total:
                        break
            except Exception:
                pass
            if len(collected) >= max_total:
                break

    return collected[:max_total]
