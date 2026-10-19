import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple, Optional

# Trusted job platforms and career domains
TRUSTED_PLATFORMS = {
    "greenhouse": {"boards.greenhouse.io", "job-boards.greenhouse.io"},
    "lever": {"jobs.lever.co"},
    "ashby": {"jobs.ashbyhq.com"},
    "workday": {"myworkdayjobs.com", "wd3.myworkday.com", "wd5.myworkday.com", "wd1.myworkday.com"},
    "smartrecruiters": {"smartrecruiters.com", "jobs.smartrecruiters.com"},
    "workable": {"workable.com", "apply.workable.com"},
    "recruitee": {"recruitee.com", "careers.bunq.com"},
    "remotive": {"remotive.com"},
    "remoteok": {"remoteok.com"},
    "arbeitnow": {"arbeitnow.com"}
}

ALLOWED_SCHEMES = {"https"}

def is_safe_ip(ip_str: str) -> bool:
    """
    Checks if an IP address is a private, loopback, link-local, multicast, or unspecified address.
    Prevents Server-Side Request Forgery (SSRF).
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return False
        if ip.version == 4 and ip in ipaddress.ip_network("100.64.0.0/10"):
            return False
        return True
    except ValueError:
        return False

def is_safe_host(hostname: str) -> bool:
    """
    Ensures hostname is not localhost, loopback, or resolving to a private/internal network IP.
    """
    if not hostname:
        return False

    lowered = hostname.lower().strip()
    if lowered in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}:
        return False

    # Check if host is raw IP literal
    try:
        raw_ip = ipaddress.ip_address(lowered)
        return is_safe_ip(str(raw_ip))
    except ValueError:
        pass

    # Resolve via DNS to verify target IP addresses
    try:
        addr_info = socket.getaddrinfo(lowered, None)
        for family, socktype, proto, canonname, sockaddr in addr_info:
            ip_str = sockaddr[0]
            if not is_safe_ip(ip_str):
                return False
        return True
    except socket.gaierror:
        # If host cannot be resolved, check if it's a domain name vs invalid
        return True
    except Exception:
        return False

def validate_external_job_url(
    url: str,
    expected_platform: Optional[str] = None,
    allow_custom_domains: bool = True
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates an external job URL against scheme, SSRF checks, and platform host rules.
    Returns (is_valid, error_message, normalized_url).
    """
    if not url or not isinstance(url, str):
        return False, "URL is missing or invalid.", None

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Malformed URL: {str(e)}", None

    # Enforce HTTPS scheme
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False, f"Disallowed scheme '{parsed.scheme}'. Only HTTPS is permitted.", None

    hostname = (parsed.hostname or "").lower().strip()
    if not hostname:
        return False, "URL missing host component.", None

    # Platform host check (performed before DNS for fast mismatch rejection)
    if expected_platform and expected_platform in TRUSTED_PLATFORMS:
        platform_hosts = TRUSTED_PLATFORMS[expected_platform]
        matches_platform = any(hostname == h or hostname.endswith(f".{h}") for h in platform_hosts)
        
        # For Workday, subdomains can be e.g. company.wd3.myworkdayjobs.com
        if expected_platform == "workday":
            matches_platform = "myworkdayjobs.com" in hostname or "myworkday.com" in hostname
        elif expected_platform == "smartrecruiters":
            matches_platform = "smartrecruiters.com" in hostname
        elif expected_platform == "workable":
            matches_platform = "workable.com" in hostname
        elif expected_platform == "recruitee":
            matches_platform = "recruitee.com" in hostname or "careers.bunq.com" in hostname

        if not matches_platform and not allow_custom_domains:
            return False, f"URL domain '{hostname}' does not match expected platform '{expected_platform}'.", None

    # Verify not resolving to private network/localhost
    if not is_safe_host(hostname):
        return False, f"Host '{hostname}' resolves to an unsafe or internal network address.", None

    return True, None, url
