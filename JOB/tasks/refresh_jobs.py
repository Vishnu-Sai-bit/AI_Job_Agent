from datetime import datetime, timezone
from typing import List, Dict, Any
from extensions import db
from models.job_source import JobSource
from models.job import Job
from collectors import get_collector_for_platform
from services.job_normalizer import JobNormalizer
from services.job_deduplicator import JobDeduplicator
from utils.url_validation import validate_external_job_url
from utils.logging_config import logger

def utc_now():
    return datetime.now(timezone.utc)

DEFAULT_SOURCES = [
    {"platform": "workday", "company_key": "nvidia", "name": "NVIDIA (Workday)"},
    {"platform": "workday", "company_key": "adobe", "name": "Adobe (Workday)"},
    {"platform": "workday", "company_key": "autodesk", "name": "Autodesk (Workday)"},
    {"platform": "greenhouse", "company_key": "gitlab", "name": "GitLab (Greenhouse)"},
    {"platform": "greenhouse", "company_key": "stripe", "name": "Stripe (Greenhouse)"},
    {"platform": "lever", "company_key": "spotify", "name": "Spotify (Lever)"},
    {"platform": "ashby", "company_key": "linear", "name": "Linear (Ashby)"},
    {"platform": "smartrecruiters", "company_key": "averydennison", "name": "Avery Dennison (SmartRecruiters)"},
    {"platform": "workable", "company_key": "skroutz", "name": "Skroutz (Workable)"},
    {"platform": "recruitee", "company_key": "bunq", "name": "bunq (Recruitee)"},
    {"platform": "remotive", "company_key": "all", "name": "Remotive Remote Jobs Feed"},
    {"platform": "arbeitnow", "company_key": "all", "name": "Arbeitnow Global Jobs Feed"},
    {"platform": "remoteok", "company_key": "all", "name": "RemoteOK Tech Jobs Feed"}
]

def ensure_default_sources():
    """Initializes standard supported job sources if table is empty."""
    for s in DEFAULT_SOURCES:
        existing = JobSource.query.filter_by(platform=s["platform"], company_key=s["company_key"]).first()
        if not existing:
            source = JobSource(
                platform=s["platform"],
                company_key=s["company_key"],
                name=s["name"],
                is_active=True
            )
            db.session.add(source)
    db.session.commit()

def run_job_refresh(limit_per_source: int = 25) -> Dict[str, Any]:
    """
    Executes end-to-end job collection pipeline:
    Source Fetch -> Normalize -> Deduplicate -> Validate URL -> Persist.
    """
    ensure_default_sources()
    active_sources = JobSource.query.filter_by(is_active=True).all()
    normalizer = JobNormalizer()
    deduplicator = JobDeduplicator()

    total_fetched = 0
    total_added = 0
    total_duplicates = 0
    total_invalid_urls = 0

    for source in active_sources:
        try:
            logger.info(f"Collecting jobs for source: {source.name} ({source.platform})")
            source.sync_status = "running"
            db.session.commit()

            collector = get_collector_for_platform(source.platform)
            raw_records = collector.fetch_jobs(source.company_key, limit=limit_per_source)
            total_fetched += len(raw_records)

            existing_jobs = Job.query.filter_by(source_platform=source.platform).all()

            for raw in raw_records:
                normalized = normalizer.normalize(raw)
                
                duplicate = deduplicator.find_duplicate(normalized, existing_jobs)
                if duplicate:
                    total_duplicates += 1
                    continue

                target_url = normalized["apply_url"] or normalized["original_url"]
                is_valid, err_msg, clean_url = validate_external_job_url(target_url, expected_platform=source.platform)
                if not is_valid:
                    logger.debug(f"Skipping job due to invalid URL: {err_msg} ({target_url})")
                    total_invalid_urls += 1
                    continue

                new_job = Job(
                    source_id=source.id,
                    source_platform=normalized["source_platform"],
                    source_company_key=normalized["source_company_key"],
                    source_job_id=normalized["source_job_id"],
                    title=normalized["title"],
                    company=normalized["company"],
                    department=normalized["department"],
                    location=normalized["location"],
                    country=normalized["country"],
                    city=normalized["city"],
                    work_mode=normalized["work_mode"],
                    employment_type=normalized["employment_type"],
                    experience_level=normalized["experience_level"],
                    salary_min=normalized["salary_min"],
                    salary_max=normalized["salary_max"],
                    currency=normalized["currency"],
                    description=normalized["description"],
                    raw_description=normalized["raw_description"],
                    required_skills=normalized["required_skills"],
                    preferred_skills=normalized["preferred_skills"],
                    original_url=normalized["original_url"],
                    apply_url=normalized["apply_url"],
                    canonical_url=normalized["canonical_url"],
                    published_at=normalized["published_at"] or utc_now(),
                    created_at=utc_now(),
                    last_verified_at=utc_now(),
                    status="active",
                    source_metadata=normalized["source_metadata"]
                )
                db.session.add(new_job)
                existing_jobs.append(new_job)
                total_added += 1

            source.sync_status = "success"
            source.last_sync_at = utc_now()
            source.sync_error = None
            db.session.commit()

        except Exception as e:
            logger.error(f"Error in job refresh for source {source.name}: {e}")
            source.sync_status = "failed"
            source.sync_error = str(e)
            db.session.commit()

    return {
        "sources_checked": len(active_sources),
        "total_fetched": total_fetched,
        "total_added": total_added,
        "total_duplicates": total_duplicates,
        "total_invalid_urls": total_invalid_urls
    }
