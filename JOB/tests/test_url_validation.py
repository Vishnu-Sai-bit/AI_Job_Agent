import pytest
from utils.url_validation import validate_external_job_url, is_safe_ip, is_safe_host

def test_safe_ip():
    assert is_safe_ip("8.8.8.8") is True
    assert is_safe_ip("1.1.1.1") is True
    assert is_safe_ip("127.0.0.1") is False
    assert is_safe_ip("10.0.0.1") is False
    assert is_safe_ip("192.168.1.1") is False
    assert is_safe_ip("169.254.169.254") is False
    assert is_safe_ip("::1") is False

def test_safe_host_localhost_blocked():
    assert is_safe_host("localhost") is False
    assert is_safe_host("127.0.0.1") is False

def test_validate_url_scheme():
    # Only HTTPS allowed
    valid, msg, _ = validate_external_job_url("http://boards.greenhouse.io/stripe/jobs/123")
    assert valid is False
    assert "Disallowed scheme" in msg

    valid, msg, _ = validate_external_job_url("javascript:alert(1)")
    assert valid is False

    valid, msg, _ = validate_external_job_url("ftp://boards.greenhouse.io/job")
    assert valid is False

def test_validate_url_ssrf_protection():
    # Internal addresses must be rejected
    valid, msg, _ = validate_external_job_url("https://127.0.0.1/admin")
    assert valid is False

    valid, msg, _ = validate_external_job_url("https://localhost:8080/jobs")
    assert valid is False

def test_validate_greenhouse_platform_url():
    valid, msg, clean_url = validate_external_job_url(
        "https://boards.greenhouse.io/gitlab/jobs/12345",
        expected_platform="greenhouse"
    )
    assert valid is True
    assert clean_url == "https://boards.greenhouse.io/gitlab/jobs/12345"

def test_validate_mismatched_platform():
    valid, msg, _ = validate_external_job_url(
        "https://evil-spoofing-site.com/jobs/123",
        expected_platform="greenhouse",
        allow_custom_domains=False
    )
    assert valid is False
    assert "does not match expected platform" in msg
