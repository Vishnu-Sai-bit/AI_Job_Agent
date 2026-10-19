import os
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

def utc_now():
    return datetime.now(timezone.utc)

# Pre-configured Workable company accounts
WORKABLE_COMPANIES = {
    "skroutz": {
        "company_name": "Skroutz",
        "account_slug": "skroutz"
    },
    "taxjar": {
        "company_name": "TaxJar",
        "account_slug": "taxjar"
    },
    "babbel": {
        "company_name": "Babbel",
        "account_slug": "babbel"
    }
}

class WorkableCollector(BaseCollector):
    platform_name = "workable"

    def __init__(self, timeout: int = 10):
        super().__init__(timeout=timeout)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })

    def fetch_jobs(self, company_key: str, limit: int = 30) -> List[RawJobRecord]:
        """
        Fetches published vacancies from Workable public widget & jobs API.
        Endpoint: https://apply.workable.com/api/v1/widget/accounts/{company_slug}
        Detail: https://apply.workable.com/api/v2/accounts/{company_slug}/jobs/{shortcode}
        """
        jobs: List[RawJobRecord] = []
        normalized_key = company_key.lower().strip()
        config = WORKABLE_COMPANIES.get(normalized_key, {})
        account_slug = config.get("account_slug") or company_key
        company_display = config.get("company_name") or company_key.replace("-", " ").title()

        endpoint = f"https://apply.workable.com/api/v1/widget/accounts/{account_slug}"

        try:
            resp = self.session.get(endpoint, timeout=self.timeout)
            if resp.status_code != 200:
                logger.info(f"Workable API returned {resp.status_code} for {account_slug}")
                return jobs

            data = resp.json()
            if not company_display and data.get("name"):
                company_display = data["name"]

            raw_jobs = data.get("jobs", [])
            for item in raw_jobs[:limit]:
                shortcode = item.get("shortcode", "").strip()
                if not shortcode:
                    continue

                title = item.get("title", "").strip()
                job_id = item.get("code") or shortcode

                # Location & work mode
                city = item.get("city", "")
                country = item.get("country", "")
                loc_str = ", ".join(filter(None, [city, country])) or "Worldwide"
                is_remote = bool(item.get("telecommuting"))
                work_mode = "remote" if is_remote else "on-site"

                # URLs
                original_url = item.get("url") or f"https://apply.workable.com/j/{shortcode}"
                apply_url = item.get("application_url") or f"https://apply.workable.com/j/{shortcode}/apply"

                # Fetch full job detail (description, requirements, salary)
                description = f"{title} position at {company_display}. Location: {loc_str}."
                raw_html = ""
                salary_min = None
                salary_max = None
                currency = None

                detail_url = f"https://apply.workable.com/api/v2/accounts/{account_slug}/jobs/{shortcode}"
                try:
                    d_resp = self.session.get(detail_url, timeout=5)
                    if d_resp.status_code == 200:
                        d_json = d_resp.json()
                        desc_html = d_json.get("description", "")
                        req_html = d_json.get("requirements", "")
                        ben_html = d_json.get("benefits", "")

                        raw_html = f"{desc_html}\n{req_html}\n{ben_html}".strip()
                        
                        clean_parts = []
                        if desc_html:
                            clean_parts.append(BeautifulSoup(desc_html, "html.parser").get_text(separator="\n").strip())
                        if req_html:
                            clean_parts.append("Requirements:\n" + BeautifulSoup(req_html, "html.parser").get_text(separator="\n").strip())
                        if ben_html:
                            clean_parts.append("Benefits:\n" + BeautifulSoup(ben_html, "html.parser").get_text(separator="\n").strip())

                        if clean_parts:
                            description = "\n\n".join(clean_parts)

                        if d_json.get("workplace"):
                            wp = d_json["workplace"].lower()
                            if "remote" in wp: work_mode = "remote"
                            elif "hybrid" in wp: work_mode = "hybrid"

                        salary_min = d_json.get("salary_from")
                        salary_max = d_json.get("salary_to")
                        currency = d_json.get("salary_currency_iso_code")
                except Exception as ex:
                    logger.debug(f"Could not fetch full Workable detail for {shortcode}: {ex}")

                job_record = RawJobRecord(
                    source_platform=self.platform_name,
                    source_company_key=normalized_key,
                    source_job_id=str(job_id),
                    title=title,
                    company=company_display,
                    location=loc_str,
                    work_mode=work_mode,
                    description=description,
                    raw_description=raw_html,
                    original_url=original_url,
                    apply_url=apply_url,
                    employment_type=item.get("employment_type") or "Full-time",
                    experience_level=item.get("experience") or "Mid",
                    salary_min=float(salary_min) if salary_min else None,
                    salary_max=float(salary_max) if salary_max else None,
                    salary_currency=currency,
                    published_at=utc_now(),
                    source_metadata={
                        "shortcode": shortcode,
                        "code": item.get("code"),
                        "department": item.get("department"),
                        "industry": item.get("industry")
                    }
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"Workable collector error for {account_slug}: {e}")

        return jobs

    def verify_job_live(self, original_url: str, apply_url: str, company_key: str = "", job_id: str = "") -> Tuple[bool, int, str]:
        """
        Verifies if a Workable posting is currently active.
        """
        target = apply_url or original_url
        try:
            resp = self.session.get(target, timeout=self.timeout, allow_redirects=True, stream=True)
            if resp.status_code == 200:
                return True, 200, "Workable application page verified live"
            elif resp.status_code in (404, 410):
                return False, resp.status_code, f"Workable page returned {resp.status_code} (Closed)"
            else:
                return True, resp.status_code, f"Workable status {resp.status_code}"
        except Exception as e:
            return False, 0, f"Workable verification error: {str(e)}"
