from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

class ArbeitnowCollector(BaseCollector):
    platform_name = "arbeitnow"

    def fetch_jobs(self, company_key: str = "all", limit: int = 50, **kwargs) -> List[RawJobRecord]:
        """
        Fetch public jobs from Arbeitnow API:
        https://www.arbeitnow.com/api/job-board-api
        """
        url = "https://www.arbeitnow.com/api/job-board-api"
        jobs: List[RawJobRecord] = []
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                logger.warning(f"Arbeitnow API returned {resp.status_code}")
                return jobs

            data = resp.json()
            job_entries = data.get("data", [])[:limit]
            for item in job_entries:
                slug = item.get("slug", "")
                title = item.get("title", "").strip()
                company_name = item.get("company_name", "").strip()
                orig_url = item.get("url", "").strip()
                
                is_remote = item.get("remote", False)
                loc = item.get("location", "")
                work_mode = "remote" if is_remote or "remote" in loc.lower() else "on-site"
                
                tags = item.get("tags", [])
                types = item.get("job_types", ["full-time"])
                emp_type = types[0] if types else "full-time"

                raw_html = item.get("description", "")
                plain_desc = BeautifulSoup(raw_html, "html.parser").get_text(separator="\n").strip() if raw_html else ""

                created_ts = item.get("created_at")
                published_at = None
                if created_ts:
                    try:
                        published_at = datetime.fromtimestamp(created_ts)
                    except Exception:
                        published_at = None

                job_record = RawJobRecord(
                    source_platform=self.platform_name,
                    source_company_key="arbeitnow-feed",
                    source_job_id=slug,
                    title=title,
                    company=company_name or "Company",
                    location=loc or "Worldwide",
                    work_mode=work_mode,
                    employment_type=emp_type,
                    description=plain_desc,
                    raw_description=raw_html,
                    required_skills=tags,
                    original_url=orig_url,
                    apply_url=orig_url,
                    published_at=published_at,
                    source_metadata={"arbeitnow_slug": slug}
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"Error fetching Arbeitnow jobs: {e}")

        return jobs
