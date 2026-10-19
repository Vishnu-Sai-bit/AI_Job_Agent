import os
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from collectors.base_collector import BaseCollector, RawJobRecord
from utils.logging_config import logger

def utc_now():
    return datetime.now(timezone.utc)

# Pre-configured SmartRecruiters enterprise boards
SMARTRECRUITERS_COMPANIES = {
    "averydennison": {
        "company_name": "Avery Dennison",
        "company_identifier": "AveryDennison"
    },
    "cern": {
        "company_name": "CERN",
        "company_identifier": "CERN"
    },
    "boschgroup": {
        "company_name": "Bosch Group",
        "company_identifier": "BoschGroup"
    },
    "square": {
        "company_name": "Square / Block",
        "company_identifier": "Square6"
    }
}

class SmartRecruitersCollector(BaseCollector):
    platform_name = "smartrecruiters"

    def __init__(self, timeout: int = 10):
        super().__init__(timeout=timeout)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })

    def fetch_jobs(self, company_key: str, limit: int = 30) -> List[RawJobRecord]:
        """
        Fetches published job postings from SmartRecruiters Public API.
        Endpoint: https://api.smartrecruiters.com/v1/companies/{company}/postings
        """
        jobs: List[RawJobRecord] = []
        normalized_key = company_key.lower().strip()
        config = SMARTRECRUITERS_COMPANIES.get(normalized_key, {})
        company_identifier = config.get("company_identifier") or company_key
        company_display = config.get("company_name") or company_key.replace("-", " ").title()

        endpoint = f"https://api.smartrecruiters.com/v1/companies/{company_identifier}/postings"
        params = {"limit": min(limit, 50)}

        try:
            resp = self.session.get(endpoint, params=params, timeout=self.timeout)
            if resp.status_code != 200:
                logger.info(f"SmartRecruiters API returned {resp.status_code} for {company_identifier}")
                return jobs

            data = resp.json()
            postings = data.get("content", [])

            for item in postings:
                job_id = str(item.get("id", "")).strip()
                if not job_id:
                    continue

                title = item.get("name", "").strip()
                ref_number = item.get("refNumber") or job_id
                
                # Location parsing
                loc_obj = item.get("location") or {}
                city = loc_obj.get("city", "")
                region = loc_obj.get("region", "")
                country = loc_obj.get("country", "")
                full_loc = loc_obj.get("fullLocation") or ", ".join(filter(None, [city, region, country])) or "Worldwide"
                
                is_remote = bool(loc_obj.get("remote"))
                is_hybrid = bool(loc_obj.get("hybrid"))
                work_mode = "remote" if is_remote else ("hybrid" if is_hybrid else "on-site")

                # Exact official posting and direct apply links
                original_url = f"https://jobs.smartrecruiters.com/{company_identifier}/{job_id}"
                apply_url = f"https://jobs.smartrecruiters.com/{company_identifier}/{job_id}/apply"

                # Fetch detailed job description and qualifications via detail endpoint
                description = f"{title} position at {company_display}. Location: {full_loc}."
                raw_html = ""
                detail_url = f"https://api.smartrecruiters.com/v1/companies/{company_identifier}/postings/{job_id}"
                try:
                    d_resp = self.session.get(detail_url, timeout=5)
                    if d_resp.status_code == 200:
                        d_json = d_resp.json()
                        sections = d_json.get("jobAd", {}).get("sections", {})
                        
                        desc_parts = []
                        raw_parts = []
                        for sec_name in ["companyDescription", "jobDescription", "qualifications", "additionalInformation"]:
                            sec_obj = sections.get(sec_name, {})
                            sec_text = sec_obj.get("text", "")
                            if sec_text:
                                raw_parts.append(sec_text)
                                clean_sec = BeautifulSoup(sec_text, "html.parser").get_text(separator="\n").strip()
                                desc_parts.append(clean_sec)

                        if desc_parts:
                            description = "\n\n".join(desc_parts)
                            raw_html = "\n".join(raw_parts)

                        if d_json.get("refNumber"):
                            ref_number = d_json["refNumber"]
                except Exception as ex:
                    logger.debug(f"Could not fetch full SmartRecruiters detail for {job_id}: {ex}")

                # Experience level & employment type
                type_emp = item.get("typeOfEmployment", {}).get("label", "Full-time") if isinstance(item.get("typeOfEmployment"), dict) else "Full-time"
                exp_lvl = item.get("experienceLevel", {}).get("label", "Mid-Senior Level") if isinstance(item.get("experienceLevel"), dict) else "Mid"

                job_record = RawJobRecord(
                    source_platform=self.platform_name,
                    source_company_key=normalized_key,
                    source_job_id=str(ref_number or job_id),
                    title=title,
                    company=company_display,
                    location=full_loc,
                    work_mode=work_mode,
                    description=description,
                    raw_description=raw_html,
                    original_url=original_url,
                    apply_url=apply_url,
                    employment_type=type_emp,
                    experience_level=exp_lvl,
                    published_at=utc_now(),
                    source_metadata={
                        "smartrecruiters_id": job_id,
                        "refNumber": ref_number,
                        "department": item.get("department", {}).get("label") if isinstance(item.get("department"), dict) else None,
                        "function": item.get("function", {}).get("label") if isinstance(item.get("function"), dict) else None
                    }
                )
                jobs.append(job_record)

        except Exception as e:
            logger.error(f"SmartRecruiters collector error for {company_identifier}: {e}")

        return jobs

    def verify_job_live(self, original_url: str, apply_url: str, company_key: str = "", job_id: str = "") -> Tuple[bool, int, str]:
        """
        Verifies if a SmartRecruiters posting is currently live and active.
        """
        # If we have company_key and job_id, verify via fast API endpoint
        if company_key and job_id:
            config = SMARTRECRUITERS_COMPANIES.get(company_key.lower(), {})
            company_identifier = config.get("company_identifier") or company_key
            api_check = f"https://api.smartrecruiters.com/v1/companies/{company_identifier}/postings/{job_id}"
            try:
                resp = self.session.get(api_check, timeout=self.timeout)
                if resp.status_code == 200:
                    return True, 200, "SmartRecruiters posting verified active via API"
                elif resp.status_code in (404, 410):
                    return False, resp.status_code, "SmartRecruiters posting closed or removed (404/410)"
            except Exception:
                pass

        target = apply_url or original_url
        try:
            resp = self.session.get(target, timeout=self.timeout, allow_redirects=True, stream=True)
            if resp.status_code == 200:
                return True, 200, "SmartRecruiters application page verified live"
            elif resp.status_code in (404, 410):
                return False, resp.status_code, f"SmartRecruiters page returned {resp.status_code} (Closed)"
            else:
                return True, resp.status_code, f"SmartRecruiters status {resp.status_code}"
        except Exception as e:
            return False, 0, f"SmartRecruiters verification error: {str(e)}"
