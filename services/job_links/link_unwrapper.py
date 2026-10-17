"""
==========================================================
AI JobAgent - Aggregator Link Unwrapper & Destination Resolver
Author : Antigravity / Beere Vishnu Sai
Follows aggregator redirect hubs (e.g. Adzuna tracking links)
to extract the underlying employer official recruitment/ATS URL.
==========================================================
"""

import requests
from urllib.parse import urlparse
from typing import Optional, Dict
from services.job_links.normalizer import is_aggregator_url, verify_ats_domain

_UNWRAPPED_URL_CACHE: Dict[str, str] = {}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def unwrap_aggregator_link(url: Optional[str]) -> str:
    """
    If the link is an aggregator redirect (e.g., Adzuna), follow redirects
    to extract the actual employer destination posting URL.
    Returns the resolved URL if successful, or original URL if unable.
    """
    if not url:
        return ""
    
    clean_url = url.strip()
    
    # Check cache first
    if clean_url in _UNWRAPPED_URL_CACHE:
        return _UNWRAPPED_URL_CACHE[clean_url]
    
    # If already a verified direct ATS domain, no need to unwrap
    if verify_ats_domain(clean_url) and not is_aggregator_url(clean_url):
        return clean_url
    
    # Only follow redirects for aggregator domains (e.g. adzuna.com/in)
    if not is_aggregator_url(clean_url):
        return clean_url

    try:
        # Use HEAD request first for fast resolution
        resp = requests.head(
            clean_url,
            allow_redirects=True,
            timeout=3.5,
            headers=DEFAULT_HEADERS
        )
        final_url = resp.url
        
        # If HEAD returned same or error, fallback to quick GET with stream
        if final_url == clean_url or resp.status_code >= 400:
            with requests.get(clean_url, allow_redirects=True, stream=True, timeout=3.5, headers=DEFAULT_HEADERS) as get_resp:
                final_url = get_resp.url
                
        if final_url and final_url != clean_url:
            _UNWRAPPED_URL_CACHE[clean_url] = final_url
            return final_url
    except Exception:
        pass

    return clean_url
