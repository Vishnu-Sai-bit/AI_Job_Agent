"""
==========================================================
AI JobAgent - Official ATS Company Board Registry
Registry of verified company board tokens and site identifiers
for free public ATS APIs (Greenhouse, Lever, Ashby).
==========================================================
"""

from typing import Dict, List, Any

# Free public ATS feeds that require ZERO API keys
COMPANY_ATS_REGISTRY: Dict[str, List[Dict[str, str]]] = {
    # 1. Greenhouse Job Board API (Public & Free)
    # Endpoint: https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true
    "greenhouse": [
        {"token": "gitlab", "name": "GitLab"},
        {"token": "dataiku", "name": "Dataiku"},
        {"token": "elastic", "name": "Elastic"},
        {"token": "stripe", "name": "Stripe"},
        {"token": "airbnb", "name": "Airbnb"},
        {"token": "databricks", "name": "Databricks"},
        {"token": "docker", "name": "Docker"},
        {"token": "canonical", "name": "Canonical"},
        {"token": "inmobi", "name": "InMobi"},
        {"token": "razorpay", "name": "Razorpay"},
        {"token": "cred", "name": "CRED"},
        {"token": "crowdstrike", "name": "CrowdStrike"},
        {"token": "figma", "name": "Figma"},
        {"token": "robinhood", "name": "Robinhood"},
        {"token": "reddit", "name": "Reddit"},
        {"token": "doordash", "name": "DoorDash"},
        {"token": "instacart", "name": "Instacart"},
    ],

    # 2. Lever Postings API (Public & Free)
    # Endpoint: https://api.lever.co/v0/postings/{site}?mode=json
    "lever": [
        {"site": "spotify", "name": "Spotify"},
        {"site": "postman", "name": "Postman"},
        {"site": "automattic", "name": "Automattic"},
        {"site": "meesho", "name": "Meesho"},
        {"site": "nykaa", "name": "Nykaa"},
        {"site": "lenskart", "name": "Lenskart"},
        {"site": "paytm", "name": "Paytm"},
        {"site": "zerodha", "name": "Zerodha"},
        {"site": "leverdemo", "name": "Lever Demo"},
    ],

    # 3. Ashby Job Postings API (Public & Free)
    # Endpoint: https://api.ashbyhq.com/posting-api/job-board/{board}
    "ashby": [
        {"board": "linear", "name": "Linear"},
        {"board": "ramp", "name": "Ramp"},
        {"board": "notion", "name": "Notion"},
        {"board": "vercel", "name": "Vercel"},
        {"board": "zapier", "name": "Zapier"},
        {"board": "retool", "name": "Retool"},
        {"board": "cursor", "name": "Cursor"},
    ]
}

def get_company_board_token(company_name: str) -> Dict[str, Any]:
    """Look up a company's known ATS provider and board token."""
    if not company_name:
        return {}
    clean_name = company_name.lower().strip()
    
    for provider, companies in COMPANY_ATS_REGISTRY.items():
        for comp in companies:
            if comp["name"].lower() == clean_name or comp.get("token", "").lower() == clean_name or comp.get("site", "").lower() == clean_name or comp.get("board", "").lower() == clean_name:
                return {
                    "ats_provider": provider.capitalize() if provider != "ashby" else "Ashby",
                    "identifier": comp.get("token") or comp.get("site") or comp.get("board"),
                    "name": comp["name"]
                }
    return {}
