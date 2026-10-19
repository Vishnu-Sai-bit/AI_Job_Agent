from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

class RemoteOKCollector(BaseCollector):
    platform_name = "remoteok"

    def fetch_jobs(self, company_key: str = "all", limit: int = 40, **kwargs) -> List[RawJobRecord]:
        """
        Fetch public remote jobs from RemoteOK API:
        https://remoteok.com/api
        """
        url = "https://remoteok.com/api"
        jobs: List[RawJobRecord] = []
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                logger.warning(f"RemoteOK API returned {resp.status_code}")
                return jobs

            data = resp.json()
            if not isinstance(data, list):
                return jobs

            # The first entry in RemoteOK response is usually legal metadata / terms
            job_entries = [d for d in data if isinstance(d, dict) and "position" in d][:limit]

            for item in job_entries:
                job_id = str(item.get("id"))
                title = item.get("position", "").strip()
                company_name = item.get("company", "").strip()
                
                orig_url = item.get("url", "")
                if orig_url and not orig_url.startswith("http"):
                    orig_url = f"https://remoteok.com{orig_url}"
                
                apply_url = item.get("apply_url", "") or orig_url
                if apply_url and not apply_url.startswith("http"):
                    apply_url = f"https://remoteok.com{apply_url}"

                loc = item.get("location", "Remote")
                tags = item.get("tags", [])
                
                raw_html = item.get("description", "")
                plain_desc = BeautifulSoup(raw_html, "html.parser").get_text(separator="\n").strip() if raw_html else ""

                date_str = item.get("date")
                published_at = None
                if date_str:
                    try:
                        published_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    except Exception:
                        published_at = None

                job_record = RawJobRecord(
                    source_platform=self.platform_name,
                    source_company_key="remoteok-feed",
                    source_job_id=job_id,
                    title=title,
                    company=company_name or "Remote Company",
                    location=loc or "Remote",
                    work_mode="remote",
                    employment_type="full-time",
                    description=plain_desc,
                    raw_description=raw_html,
                    required_skills=tags,
                    original_url=orig_url,
                    apply_url=apply_url,
                    published_at=published_at,
                    source_metadata={"remoteok_id": job_id, "epoch": item.get("epoch")}
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"Error fetching RemoteOK jobs: {e}")

        return jobs
