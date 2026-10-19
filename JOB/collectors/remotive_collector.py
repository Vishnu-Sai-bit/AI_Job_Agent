from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

class RemotiveCollector(BaseCollector):
    platform_name = "remotive"

    def fetch_jobs(self, company_key: str = "all", limit: int = 50, **kwargs) -> List[RawJobRecord]:
        """
        Fetch public remote jobs from Remotive API:
        https://remotive.com/api/remote-jobs?limit=50
        Attributes source to Remotive and preserves original posting URL.
        """
        url = f"https://remotive.com/api/remote-jobs?limit={limit}"
        jobs: List[RawJobRecord] = []
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                logger.warning(f"Remotive API returned {resp.status_code}")
                return jobs

            data = resp.json()
            job_entries = data.get("jobs", [])
            for item in job_entries:
                job_id = str(item.get("id"))
                title = item.get("title", "").strip()
                company_name = item.get("company_name", "").strip()
                orig_url = item.get("url", "").strip()
                apply_url = orig_url  # Remotive posting page includes direct apply modal/link
                
                req_loc = item.get("candidate_required_location", "Worldwide")
                tags = item.get("tags", [])
                
                raw_html = item.get("description", "")
                plain_desc = BeautifulSoup(raw_html, "html.parser").get_text(separator="\n").strip() if raw_html else ""
                
                pub_date_str = item.get("publication_date")
                published_at = None
                if pub_date_str:
                    try:
                        published_at = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                    except Exception:
                        published_at = None

                job_record = RawJobRecord(
                    source_platform=self.platform_name,
                    source_company_key="remotive-feed",
                    source_job_id=job_id,
                    title=title,
                    company=company_name or "Remote Company",
                    department=item.get("category", ""),
                    location=req_loc,
                    work_mode="remote",
                    employment_type=item.get("job_type", "full-time").replace("_", "-"),
                    description=plain_desc,
                    raw_description=raw_html,
                    required_skills=tags,
                    original_url=orig_url,
                    apply_url=apply_url,
                    published_at=published_at,
                    source_metadata={"remotive_id": job_id, "salary": item.get("salary", "")}
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"Error fetching Remotive jobs: {e}")

        return jobs
