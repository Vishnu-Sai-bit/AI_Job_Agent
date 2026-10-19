import pytest
from collectors.base_collector import RawJobRecord
from services.job_normalizer import JobNormalizer

def test_job_normalizer_remotive_payload():
    normalizer = JobNormalizer()
    raw = RawJobRecord(
        source_platform="remotive",
        source_company_key="remotive-feed",
        source_job_id="9912",
        title="Senior Python Backend Engineer [Remote]",
        company="Global SaaS",
        location="Worldwide",
        work_mode="remote",
        employment_type="full_time",
        description="Looking for an experienced engineer in Python, Flask, and PostgreSQL. Preferred: Docker.",
        original_url="https://remotive.com/remote-jobs/software-dev/senior-python-engineer-9912?utm_source=feed",
        apply_url="https://remotive.com/remote-jobs/software-dev/senior-python-engineer-9912?utm_source=feed"
    )

    norm = normalizer.normalize(raw)
    assert norm["title"] == "Senior Python Backend Engineer"
    assert norm["work_mode"] == "remote"
    assert norm["source_platform"] == "remotive"
    assert "utm_source" not in norm["apply_url"]  # Tracking query parameters cleaned
    assert "Python" in norm["required_skills"]
    assert "Flask" in norm["required_skills"]

def test_job_normalizer_greenhouse_payload():
    normalizer = JobNormalizer()
    raw = RawJobRecord(
        source_platform="greenhouse",
        source_company_key="gitlab",
        source_job_id="48201",
        title="Backend Engineer, Database",
        company="GitLab",
        location="Remote, Global",
        work_mode="remote",
        description="Join GitLab to build PostgreSQL query optimizations and Ruby services.",
        original_url="https://boards.greenhouse.io/gitlab/jobs/48201",
        apply_url="https://boards.greenhouse.io/gitlab/jobs/48201#app"
    )

    norm = normalizer.normalize(raw)
    assert norm["company"] == "GitLab"
    assert norm["source_job_id"] == "48201"
    assert norm["apply_url"].endswith("#app")
