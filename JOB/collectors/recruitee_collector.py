import os
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

def utc_now():
    return datetime.now(timezone.utc)

# Pre-configured Recruitee companies
RECRUITEE_COMPANIES = {
    "bunq": {
        "company_name": "bunq",
        "company_slug": "bunq"
    }
}

class RecruiteeCollector(BaseCollector):
    platform_name = "recruitee"

    def __init__(self, timeout: int = 10):
        super().__init__(timeout=timeout)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })

    def fetch_jobs(self, company_key: str, limit: int = 30) -> List[RawJobRecord]:
        """
        Fetches published vacancies from Recruitee public API.
        Endpoint: https://{company_slug}.recruitee.com/api/offers/
        """
        jobs: List[RawJobRecord] = []
        normalized_key = company_key.lower().strip()
        config = RECRUITEE_COMPANIES.get(normalized_key, {})
        company_slug = config.get("company_slug") or company_key
        company_display = config.get("company_name") or company_key.replace("-", " ").title()

        endpoint = f"https://{company_slug}.recruitee.com/api/offers/"

        try:
            resp = self.session.get(endpoint, timeout=self.timeout)
            if resp.status_code != 200:
                logger.info(f"Recruitee API returned {resp.status_code} for {company_slug}")
                return jobs

            data = resp.json()
            offers = data.get("offers", [])

            for item in offers[:limit]:
                job_id = str(item.get("id", "")).strip()
                if not job_id:
                    continue

                title = item.get("title", "").strip()
                slug = item.get("slug", "")

                # Location & work mode
                city = item.get("city", "") or item.get("location", "")
                country = item.get("country", "")
                loc_str = ", ".join(filter(None, [city, country])) or "Worldwide"
                is_remote = bool(item.get("remote"))
                work_mode = "remote" if is_remote else "on-site"

                # URLs
                careers_url = item.get("careers_url") or f"https://{company_slug}.recruitee.com/o/{slug}"
                apply_url = f"{careers_url}/new" if "/o/" in careers_url else careers_url

                # Clean description and requirements
                desc_html = item.get("description", "") or ""
                req_html = item.get("requirements", "") or ""
                raw_html = f"{desc_html}\n{req_html}".strip()

                clean_desc = BeautifulSoup(desc_html, "html.parser").get_text(separator="\n").strip() if desc_html else ""
                clean_req = BeautifulSoup(req_html, "html.parser").get_text(separator="\n").strip() if req_html else ""
                
                full_description = f"{title} position at {company_display}."
                if clean_desc or clean_req:
                    parts = []
                    if clean_desc: parts.append(clean_desc)
                    if clean_req: parts.append(f"Requirements:\n{clean_req}")
                    full_description = "\n\n".join(parts)

                job_record = RawJobRecord(
                    source_platform=self.platform_name,
                    source_company_key=normalized_key,
                    source_job_id=str(job_id),
                    title=title,
                    company=company_display,
                    location=loc_str,
                    work_mode=work_mode,
                    description=full_description,
                    raw_description=raw_html,
                    original_url=careers_url,
                    apply_url=apply_url,
                    published_at=utc_now(),
                    source_metadata={
                        "recruitee_id": job_id,
                        "slug": slug,
                        "department": item.get("department"),
                        "min_hours": item.get("min_hours"),
                        "max_hours": item.get("max_hours")
                    }
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"Recruitee collector error for {company_slug}: {e}")

        return jobs

    def verify_job_live(self, original_url: str, apply_url: str, company_key: str = "", job_id: str = "") -> Tuple[bool, int, str]:
        """
        Verifies if a Recruitee offer is currently live.
        """
        target = apply_url or original_url
        try:
            resp = self.session.get(target, timeout=self.timeout, allow_redirects=True, stream=True)
            if resp.status_code == 200:
                return True, 200, "Recruitee offer page verified live"
            elif resp.status_code in (404, 410):
                return False, resp.status_code, f"Recruitee page returned {resp.status_code} (Closed)"
            else:
                return True, resp.status_code, f"Recruitee status {resp.status_code}"
        except Exception as e:
            return False, 0, f"Recruitee verification error: {str(e)}"
