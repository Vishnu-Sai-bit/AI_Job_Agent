"""
==========================================================
AI JobAgent - ATS Job Synchronizer
Reads registry.json, queries supported ATS connectors,
and synchronizes vacancies into SQLite discovered_jobs table.
Records individual company failures without halting execution.
==========================================================
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure project root is in sys.path when executed directly as script
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.job_sources.connectors import CONNECTORS
from services.job_sources.url_verifier import verify_destination_url
from repositories.job_repository import (
    initialize_jobs_table,
    save_job,
    get_default_db_path,
    mark_job_verified,
)
from utils import info, warning, error

REGISTRY_PATH = ROOT / "services" / "job_sources" / "registry.json"


def sync_all_companies(
    db_path: Optional[str] = None,
    registry_path: Optional[Path] = None,
    max_per_company: int = 50,
    verify_urls: bool = False,
) -> Dict[str, Any]:
    """
    Synchronize all registered companies across Greenhouse, Lever, Ashby,
    SmartRecruiters, and Workable into the discovered_jobs database.
    """
    target_registry = registry_path or REGISTRY_PATH
    if not target_registry.exists():
        warning(f"Company registry file not found at {target_registry}")
        return {"success": False, "error": f"Registry not found: {target_registry}"}

    with target_registry.open("r", encoding="utf-8") as file:
        companies = json.load(file)

    target_db = Path(db_path) if db_path else get_default_db_path()
    initialize_jobs_table(str(target_db))

    summary: Dict[str, Any] = {
        "total_companies_registered": len(companies),
        "total_companies_polled": 0,
        "total_jobs_saved": 0,
        "companies": {},
        "errors": {},
    }

    with sqlite3.connect(str(target_db)) as conn:
        for comp in companies:
            comp_name = comp.get("company", "Unknown")
            provider = comp.get("provider", "").lower().strip()
            connector = CONNECTORS.get(provider)

            if connector is None:
                err_msg = f"Unsupported ATS provider '{provider}'"
                summary["errors"][comp_name] = err_msg
                warning(f"[{comp_name}] {err_msg}")
                continue

            summary["total_companies_polled"] += 1
            comp_count = 0

            try:
                info(f"Synchronizing vacancies for {comp_name} via {provider}...")
                for job in connector(comp):
                    if max_per_company and comp_count >= max_per_company:
                        break

                    saved = save_job(conn, job)
                    if saved:
                        comp_count += 1
                        summary["total_jobs_saved"] += 1

                        if verify_urls:
                            res = verify_destination_url(job.get("apply_url") or job.get("official_job_url"))
                            if res.get("is_verified"):
                                mark_job_verified(job.get("external_job_id"), verified=True, conn_or_path=conn)

                conn.commit()
                summary["companies"][comp_name] = {
                    "provider": provider,
                    "vacancies_synced": comp_count,
                    "status": "success",
                }
                info(f"[{comp_name}] Successfully synced {comp_count} vacancies.")
            except Exception as e:
                err_str = str(e)
                summary["errors"][comp_name] = err_str
                summary["companies"][comp_name] = {
                    "provider": provider,
                    "vacancies_synced": comp_count,
                    "status": "error",
                    "error": err_str,
                }
                warning(f"[{comp_name}] Synchronization encountered notice: {err_str}")

    return summary


if __name__ == "__main__":
    print("=" * 60)
    print("AI JobAgent - Multi-Source ATS Synchronizer")
    print("=" * 60)
    results = sync_all_companies(verify_urls=False)
    print(f"\nCompanies Polled : {results['total_companies_polled']} / {results['total_companies_registered']}")
    print(f"Total Vacancies  : {results['total_jobs_saved']}")
    if results.get("errors"):
        print(f"Notices/Errors   : {len(results['errors'])}")
        for comp, err in results["errors"].items():
            print(f"  * {comp}: {err}")
    print("\nSynchronization completed successfully.")
