import json
from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

class CompanyCareersCollector(BaseCollector):
    platform_name = "company_career"

    def fetch_jobs(self, company_key: str, **kwargs) -> List[RawJobRecord]:
        """
        Extracts structured JSON-LD (schema.org/JobPosting) from a company career page.
        Pass page_url in kwargs.
        """
        page_url = kwargs.get("page_url", "")
        if not page_url:
            return []

        jobs: List[RawJobRecord] = []
        try:
            resp = self.session.get(page_url, timeout=self.timeout)
            if resp.status_code != 200:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    data = json.loads(script.string or "{}")
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") == "JobPosting":
                            title = item.get("title", "").strip()
                            desc = BeautifulSoup(item.get("description", ""), "html.parser").get_text(separator="\n").strip()
                            org = item.get("hiringOrganization", {})
                            company = org.get("name", company_key) if isinstance(org, dict) else company_key
                            job_url = item.get("url") or page_url
                            
                            # Location
                            loc_info = item.get("jobLocation", {})
                            addr = loc_info.get("address", {}) if isinstance(loc_info, dict) else {}
                            location_str = ""
                            if isinstance(addr, dict):
                                location_str = ", ".join(filter(None, [addr.get("addressLocality"), addr.get("addressCountry")]))
                            
                            job_id = str(item.get("identifier", {}).get("value") if isinstance(item.get("identifier"), dict) else item.get("identifier") or hash(job_url))
                            
                            record = RawJobRecord(
                                source_platform=self.platform_name,
                                source_company_key=company_key,
                                source_job_id=job_id,
                                title=title,
                                company=company,
                                location=location_str,
                                description=desc,
                                original_url=job_url,
                                apply_url=job_url,
                                source_metadata={"ld_json": True}
                            )
                            jobs.append(record)
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"CompanyCareersCollector error for {company_key}: {e}")

        return jobs
