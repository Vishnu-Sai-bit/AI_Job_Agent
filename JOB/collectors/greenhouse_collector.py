from datetime import datetime
from typing import List, Tuple
from bs4 import BeautifulSoup
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

class GreenhouseCollector(BaseCollector):
    platform_name = "greenhouse"

    def fetch_jobs(self, company_key: str, **kwargs) -> List[RawJobRecord]:
        """
        Fetch public jobs from Greenhouse Job Board API:
        https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true
        """
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_key}/jobs?content=true"
        jobs: List[RawJobRecord] = []
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                logger.warning(f"Greenhouse API returned {resp.status_code} for company {company_key}")
                return jobs

            data = resp.json()
            job_entries = data.get("jobs", [])
            for item in job_entries:
                job_id = str(item.get("id"))
                title = item.get("title", "").strip()
                abs_url = item.get("absolute_url", "").strip()
                apply_url = f"{abs_url}#app" if abs_url and "#app" not in abs_url else abs_url
                
                # Clean HTML content
                raw_html = item.get("content", "")
                plain_desc = BeautifulSoup(raw_html, "html.parser").get_text(separator="\n").strip() if raw_html else ""
                
                # Location & Department
                loc_obj = item.get("location", {})
                location_name = loc_obj.get("name", "") if isinstance(loc_obj, dict) else str(loc_obj)
                work_mode = "remote" if "remote" in location_name.lower() or "remote" in title.lower() else "on-site"
                
                departments = [d.get("name") for d in item.get("departments", []) if d.get("name")]
                dept_str = ", ".join(departments)

                updated_at_str = item.get("updated_at")
                published_at = None
                if updated_at_str:
                    try:
                        published_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                    except Exception:
                        published_at = None

                job_record = RawJobRecord(
                    source_platform=self.platform_name,
                    source_company_key=company_key,
                    source_job_id=job_id,
                    title=title,
                    company=company_key.replace("-", " ").title(),
                    department=dept_str,
                    location=location_name,
                    work_mode=work_mode,
                    description=plain_desc,
                    raw_description=raw_html,
                    original_url=abs_url,
                    apply_url=apply_url,
                    published_at=published_at,
                    source_metadata={"greenhouse_id": job_id, "updated_at": updated_at_str}
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"Error fetching Greenhouse jobs for {company_key}: {e}")

        return jobs

    def verify_job_live(self, original_url: str, apply_url: str, company_key: str = "", job_id: str = "") -> Tuple[bool, int, str]:
        """
        Verify single Greenhouse posting via public single-job endpoint if available.
        """
        if company_key and job_id:
            api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_key}/jobs/{job_id}"
            try:
                resp = self.session.get(api_url, timeout=self.timeout)
                if resp.status_code == 200:
                    return True, 200, "Greenhouse API confirmed posting active"
                elif resp.status_code == 404:
                    return False, 404, "Greenhouse API reported job closed or deleted"
            except Exception as e:
                logger.debug(f"Direct API check failed, falling back to HTTP check: {e}")

        return super().verify_job_live(original_url, apply_url)
