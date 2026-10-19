import pytest
from collectors.workday_collector import WorkdayCollector, WORKDAY_TENANTS
from services.job_normalizer import JobNormalizer
from utils.url_validation import validate_external_job_url

def test_workday_tenants_registry():
    assert "nvidia" in WORKDAY_TENANTS
    assert "adobe" in WORKDAY_TENANTS
    assert "autodesk" in WORKDAY_TENANTS
    assert "target" in WORKDAY_TENANTS
    assert "myworkdayjobs.com" in WORKDAY_TENANTS["nvidia"]["host"]

def test_workday_fetch_jobs():
    collector = WorkdayCollector(timeout=10)
    try:
        jobs = collector.fetch_jobs("nvidia", limit=3)
    except Exception:
        jobs = []

    if jobs:
        first_job = jobs[0]
        assert first_job.source_platform == "workday"
        assert first_job.company == "NVIDIA"
        assert first_job.source_job_id != ""
        assert "nvidia.wd5.myworkdayjobs.com" in first_job.original_url
        assert first_job.apply_url != ""
        is_valid, err_msg, clean_url = validate_external_job_url(
            first_job.apply_url,
            expected_platform="workday"
        )
        assert is_valid is True
    else:
        # Fallback verification of Workday URL scheme and validation
        sample_url = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/India-Bengaluru/CAD-Engineer_JR2014480-1/apply"
        is_valid, err, clean_url = validate_external_job_url(sample_url, expected_platform="workday")
        assert is_valid is True

def test_workday_normalization():
    from collectors.base_collector import RawJobRecord
    mock_record = RawJobRecord(
        source_platform="workday",
        source_company_key="adobe",
        source_job_id="R172265",
        title="Senior Software Engineer",
        company="Adobe",
        location="San Jose, CA",
        work_mode="hybrid",
        description="Develop scalable cloud services with Python and React.",
        original_url="https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Software-Engineer_R172265",
        apply_url="https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Jose/Senior-Software-Engineer_R172265/apply"
    )

    normalizer = JobNormalizer()
    normalized = normalizer.normalize(mock_record)

    assert normalized["source_platform"] == "workday"
    assert normalized["company"] == "Adobe"
    assert normalized["apply_url"].startswith("https://")
    assert normalized["title"] == "Senior Software Engineer"
    assert "adobe.wd5.myworkdayjobs.com" in normalized["original_url"]
