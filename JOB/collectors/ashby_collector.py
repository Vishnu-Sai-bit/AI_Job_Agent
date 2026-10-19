from datetime import datetime
from typing import List
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

class AshbyCollector(BaseCollector):
    platform_name = "ashby"

    def fetch_jobs(self, company_key: str, **kwargs) -> List[RawJobRecord]:
        """
        Fetch public jobs from Ashby Job Board API:
        https://api.ashbyhq.com/posting-api/job-board/{company}
        """
        url = f"https://api.ashbyhq.com/posting-api/job-board/{company_key}"
        jobs: List[RawJobRecord] = []
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                logger.warning(f"Ashby API returned {resp.status_code} for company {company_key}")
                return jobs

            data = resp.json()
            job_entries = data.get("jobs", [])
            for item in job_entries:
                job_id = str(item.get("id"))
                title = item.get("title", "").strip()
                job_url = item.get("jobUrl", "").strip()
                apply_url = item.get("applyUrl", "").strip() or job_url
                
                is_remote = item.get("isRemote", False)
                location_name = item.get("locationName", "")
                work_mode = "remote" if is_remote or "remote" in location_name.lower() else "on-site"
                
                plain_desc = item.get("descriptionPlain", "") or ""
                raw_html = item.get("descriptionHtml", "") or ""
                dept_name = item.get("department", "") or ""
                emp_type = item.get("employmentType", "full-time").lower()

                published_at_str = item.get("publishedAt")
                published_at = None
                if published_at_str:
                    try:
                        published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
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
                    employment_type=emp_type,
                    description=plain_desc,
                    raw_description=raw_html,
                    original_url=job_url,
                    apply_url=apply_url,
                    published_at=published_at,
                    source_metadata={"ashby_id": job_id}
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"Error fetching Ashby jobs for {company_key}: {e}")

        return jobs
