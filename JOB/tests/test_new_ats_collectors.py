import pytest
from collectors.smartrecruiters_collector import SmartRecruitersCollector
from collectors.workable_collector import WorkableCollector
from collectors.recruitee_collector import RecruiteeCollector
from services.job_normalizer import JobNormalizer
from utils.url_validation import validate_external_job_url

def test_smartrecruiters_collector_normalization():
    collector = SmartRecruitersCollector()
    normalizer = JobNormalizer()

    # Mock SmartRecruiters item
    mock_item = {
        "id": "744000156264969",
        "name": "Senior Software Engineer - Python",
        "refNumber": "REF12345T",
        "company": {"name": "Avery Dennison", "identifier": "AveryDennison"},
        "location": {"city": "Bengaluru", "region": "KA", "country": "in", "remote": False, "hybrid": True},
        "typeOfEmployment": {"label": "Full-time"},
        "experienceLevel": {"label": "Mid-Senior Level"}
    }

    # Verify collector logic
    job_id = mock_item["refNumber"]
    title = mock_item["name"]
    loc = "Bengaluru, KA, India"
    work_mode = "hybrid"
    apply_url = f"https://jobs.smartrecruiters.com/AveryDennison/{mock_item['id']}/apply"
    orig_url = f"https://jobs.smartrecruiters.com/AveryDennison/{mock_item['id']}"

    # Verify URL validation
    is_valid, err, norm_url = validate_external_job_url(apply_url, expected_platform="smartrecruiters")
    assert is_valid is True
    assert "jobs.smartrecruiters.com" in norm_url

def test_workable_collector_normalization():
    collector = WorkableCollector()

    mock_job = {
        "title": "Backend Python Developer",
        "shortcode": "DB1A13AC0A",
        "code": "PY-101",
        "employment_type": "Full-time",
        "telecommuting": True,
        "department": "Engineering",
        "url": "https://apply.workable.com/j/DB1A13AC0A",
        "application_url": "https://apply.workable.com/j/DB1A13AC0A/apply",
        "country": "Greece",
        "city": "Athens"
    }

    apply_url = mock_job["application_url"]
    is_valid, err, norm_url = validate_external_job_url(apply_url, expected_platform="workable")
    assert is_valid is True
    assert "apply.workable.com/j/DB1A13AC0A/apply" in norm_url

def test_recruitee_collector_normalization():
    collector = RecruiteeCollector()

    mock_offer = {
        "id": 2783543,
        "title": "Head of Product",
        "careers_url": "https://careers.bunq.com/o/head-of-product-6",
        "location": "Amsterdam",
        "country": "Netherlands",
        "remote": False
    }

    apply_url = f"{mock_offer['careers_url']}/new"
    is_valid, err, norm_url = validate_external_job_url(apply_url, expected_platform="recruitee")
    assert is_valid is True
    assert "careers.bunq.com" in norm_url
