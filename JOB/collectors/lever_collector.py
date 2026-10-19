from datetime import datetime
from typing import List, Tuple
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

class LeverCollector(BaseCollector):
    platform_name = "lever"

    def fetch_jobs(self, company_key: str, **kwargs) -> List[RawJobRecord]:
        """
        Fetch public jobs from Lever Postings API:
        https://api.lever.co/v0/postings/{company}?mode=json
        """
        url = f"https://api.lever.co/v0/postings/{company_key}?mode=json"
        jobs: List[RawJobRecord] = []
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                logger.warning(f"Lever API returned {resp.status_code} for company {company_key}")
                return jobs

            entries = resp.json()
            if not isinstance(entries, list):
                return jobs

            for item in entries:
                job_id = str(item.get("id"))
                title = item.get("text", "").strip()
                hosted_url = item.get("hostedUrl", "").strip()
                apply_url = item.get("applyUrl", "").strip() or hosted_url
                
                categories = item.get("categories", {}) or {}
                location_name = categories.get("location", "")
                dept_name = categories.get("department", "") or categories.get("team", "")
                commitment = categories.get("commitment", "full-time").lower()
                
                work_mode = "remote" if "remote" in location_name.lower() or "remote" in title.lower() else "on-site"

                plain_desc = item.get("descriptionPlain", "") or ""
                raw_html = item.get("description", "") or ""

                created_ts = item.get("createdAt")
                published_at = None
                if created_ts:
                    try:
                        published_at = datetime.fromtimestamp(created_ts / 1000.0)
                    except Exception:
                        published_at = None

                job_record = RawJobRecord(
                    source_platform=self.platform_name,
                    source_company_key=company_key,
                    source_job_id=job_id,
                    title=title,
                    company=company_key.replace("-", " ").title(),
                    department=dept_name,
                    location=location_name,
                    work_mode=work_mode,
                    employment_type=commitment,
                    description=plain_desc,
                    raw_description=raw_html,
                    original_url=hosted_url,
                    apply_url=apply_url,
                    published_at=published_at,
                    source_metadata={"lever_id": job_id, "categories": categories}
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"Error fetching Lever jobs for {company_key}: {e}")

        return jobs

    def verify_job_live(self, original_url: str, apply_url: str, company_key: str = "", job_id: str = "") -> Tuple[bool, int, str]:
        """
        Verify single Lever posting via public single-job endpoint if available.
        """
        if company_key and job_id:
            api_url = f"https://api.lever.co/v0/postings/{company_key}/{job_id}"
            try:
                resp = self.session.get(api_url, timeout=self.timeout)
                if resp.status_code == 200:
                    return True, 200, "Lever API confirmed posting active"
                elif resp.status_code == 404:
                    return False, 404, "Lever API reported job closed or deleted"
            except Exception as e:
                logger.debug(f"Direct Lever API check failed: {e}")

        return super().verify_job_live(original_url, apply_url)
