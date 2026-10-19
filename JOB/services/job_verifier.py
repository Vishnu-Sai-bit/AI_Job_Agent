from datetime import datetime, timezone
from typing import Tuple, Optional
import requests
from extensions import db
from models.job import Job, VerificationLog
from utils.url_validation import validate_external_job_url, is_safe_host
from collectors import get_collector_for_platform
from utils.logging_config import logger

def utc_now():
    return datetime.now(timezone.utc)

class JobVerifier:
    def __init__(self, timeout: int = 6, max_redirects: int = 5):
        self.timeout = timeout
        self.max_redirects = max_redirects

    def verify_job(self, job: Job) -> Tuple[bool, str]:
        """
        Runs link and availability verification for a job posting.
        Logs result in VerificationLog and updates job.status and job.last_verified_at.
        Returns (is_active, message).
        """
        target_url = job.apply_url or job.original_url
        is_valid_url, err_msg, _ = validate_external_job_url(target_url, expected_platform=job.source_platform)
        if not is_valid_url:
            self._record_log(job, "host_disallowed", 0, target_url, err_msg or "Disallowed host or unsafe scheme")
            job.status = "unavailable"
            job.last_verified_at = utc_now()
            db.session.commit()
            return False, f"URL validation failed: {err_msg}"

        is_active = True
        status_code = 200
        details = "Verified active"

        try:
            collector = get_collector_for_platform(job.source_platform)
            if hasattr(collector, "verify_job_live"):
                is_active, status_code, details = collector.verify_job_live(
                    original_url=job.original_url,
                    apply_url=job.apply_url,
                    company_key=job.source_company_key,
                    job_id=job.source_job_id
                )
            else:
                is_active, status_code, details = self._http_verify(target_url)
        except Exception as e:
            is_active, status_code, details = self._http_verify(target_url)

        result_type = "active" if is_active else ("closed" if status_code in (404, 410) else "http_error")
        job.status = "active" if is_active else "closed"
        job.last_verified_at = utc_now()

        self._record_log(job, result_type, status_code, target_url, details)
        db.session.commit()
        return is_active, details

    def _http_verify(self, url: str) -> Tuple[bool, int, str]:
        """
        Follows redirects safely, verifying each step against SSRF and HTTPS.
        """
        current_url = url
        session = requests.Session()
        session.headers.update({"User-Agent": "AIJobAgent/1.0-Verifier"})

        try:
            for _ in range(self.max_redirects):
                valid, msg, _ = validate_external_job_url(current_url)
                if not valid:
                    return False, 0, f"Unsafe redirect destination: {msg}"

                resp = session.get(current_url, timeout=self.timeout, allow_redirects=False, stream=True)
                if resp.status_code in (301, 302, 303, 307, 308):
                    loc = resp.headers.get("Location")
                    if not loc:
                        break
                    if loc.startswith("/"):
                        from urllib.parse import urljoin
                        current_url = urljoin(current_url, loc)
                    else:
                        current_url = loc
                    continue

                if resp.status_code == 200:
                    return True, 200, "Destination reachable and active"
                elif resp.status_code in (404, 410):
                    return False, resp.status_code, "Job posting expired or not found (404/410)"
                else:
                    return True, resp.status_code, f"Status code {resp.status_code}"

            return True, 200, "Redirect chain completed"
        except requests.exceptions.RequestException as e:
            return False, 0, f"HTTP request failed: {str(e)}"

    def _record_log(self, job: Job, result: str, http_status: int, dest_url: str, details: str):
        log = VerificationLog(
            job_id=job.id,
            result=result,
            http_status=http_status,
            destination_url=dest_url,
            details=details,
            checked_at=utc_now()
        )
        db.session.add(log)
