from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

def utc_now():
    return datetime.now(timezone.utc)

# Well-known Workday tenants with verified CXS career endpoints
WORKDAY_TENANTS: Dict[str, Dict[str, str]] = {
    "nvidia": {
        "host": "nvidia.wd5.myworkdayjobs.com",
        "tenant": "nvidia",
        "site": "NVIDIAExternalCareerSite",
        "company_name": "NVIDIA"
    },
    "adobe": {
        "host": "adobe.wd5.myworkdayjobs.com",
        "tenant": "adobe",
        "site": "external_experienced",
        "company_name": "Adobe"
    },
    "autodesk": {
        "host": "autodesk.wd1.myworkdayjobs.com",
        "tenant": "autodesk",
        "site": "Ext",
        "company_name": "Autodesk"
    },
    "target": {
        "host": "target.wd5.myworkdayjobs.com",
        "tenant": "target",
        "site": "targetcareers",
        "company_name": "Target"
    }
}

class WorkdayCollector(BaseCollector):
    platform_name = "workday"

    def fetch_jobs(self, company_key: str, limit: int = 20, **kwargs) -> List[RawJobRecord]:
        """
        Workday provider adapter.
        Queries modern Workday CXS search endpoint and retrieves official job postings.
        """
        tenant_info = WORKDAY_TENANTS.get(company_key.lower(), {})
        config = kwargs.get("config", {}) or tenant_info

        host = config.get("host") or f"{company_key}.myworkdayjobs.com"
        tenant = config.get("tenant") or company_key
        site = config.get("site") or f"{company_key}Careers"
        company_display = config.get("company_name") or company_key.replace("-", " ").title()

        endpoint = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        payload = {
            "appliedFacets": {},
            "limit": min(limit, 30),
            "offset": 0,
            "searchText": ""
        }

        jobs: List[RawJobRecord] = []
        try:
            resp = self.session.post(endpoint, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code != 200:
                logger.info(f"Workday CXS API returned status {resp.status_code} for {host}")
                return jobs

            data = resp.json()
            postings = data.get("jobPostings", [])

            for item in postings:
                title = item.get("title", "").strip()
                ext_path = item.get("externalPath", "")
                
                # Extract requisition / job ID
                bullet_fields = item.get("bulletFields", [])
                job_id = bullet_fields[0] if bullet_fields else ""
                if not job_id and ext_path:
                    job_id = ext_path.split("_")[-1] if "_" in ext_path else ext_path.strip("/")
                if not job_id:
                    job_id = str(abs(hash(ext_path)))

                base_site_url = f"https://{host}/en-US/{site}"
                clean_path = ext_path.lstrip("/")
                original_url = f"https://{host}/{site}/{clean_path}"
                apply_url = f"https://{host}/{site}/{clean_path}/apply"
                
                loc = item.get("locationsText", "")
                work_mode = "remote" if "remote" in loc.lower() or "remote" in title.lower() else "on-site"

                # Attempt to fetch full description via CXS detail endpoint
                description = f"Workday posting for {title} at {company_display}. Location: {loc}."
                raw_html = ""
                detail_endpoint = f"https://{host}/wday/cxs/{tenant}/{site}{ext_path}"
                try:
                    detail_resp = self.session.get(detail_endpoint, headers=headers, timeout=5)
                    if detail_resp.status_code == 200:
                        detail_data = detail_resp.json()
                        info = detail_data.get("jobPostingInfo", {})
                        if info.get("externalUrl"):
                            original_url = info["externalUrl"]
                            apply_url = f"{original_url}/apply"
                        raw_desc = info.get("jobDescription", "")
                        if raw_desc:
                            raw_html = raw_desc
                            description = BeautifulSoup(raw_desc, "html.parser").get_text(separator="\n").strip()
                        if info.get("timeType"):
                            emp_type = info["timeType"].lower()
                        if info.get("location"):
                            loc = info["location"]
                except Exception as ex:
                    logger.debug(f"Could not fetch full Workday detail for {job_id}: {ex}")

                job_record = RawJobRecord(
                    source_platform=self.platform_name,
                    source_company_key=company_key.lower(),
                    source_job_id=str(job_id),
                    title=title,
                    company=company_display,
                    location=loc or "Worldwide",
                    work_mode=work_mode,
                    description=description,
                    raw_description=raw_html,
                    original_url=original_url,
                    apply_url=apply_url,
                    published_at=utc_now(),
                    source_metadata={
                        "workday_ext_path": ext_path,
                        "postedOn": item.get("postedOn"),
                        "bulletFields": bullet_fields,
                        "host": host,
                        "site": site,
                        "tenant": tenant
                    }
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"Workday collector error for {company_key}: {e}")

        return jobs

    def verify_job_live(self, original_url: str, apply_url: str, company_key: str = "", job_id: str = "") -> Tuple[bool, int, str]:
        """
        Verify availability of Workday posting.
        """
        target = apply_url or original_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            resp = self.session.get(target, headers=headers, timeout=self.timeout, allow_redirects=True, stream=True)
            if resp.status_code == 200:
                return True, 200, "Workday job posting verified live"
            elif resp.status_code in (404, 410):
                return False, resp.status_code, f"Workday posting returned {resp.status_code} (Closed or Removed)"
            else:
                return True, resp.status_code, f"Workday returned status {resp.status_code}"
        except Exception as e:
            return False, 0, f"Workday verification error: {str(e)}"
