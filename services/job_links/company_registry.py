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
    # 1. Workday (Enterprise HCM / ATS)
    "workday": [
        {"tenant": "cisco", "domain": "cisco.wd5.myworkdayjobs.com", "name": "Cisco"},
        {"tenant": "salesforce", "domain": "salesforce.wd12.myworkdayjobs.com", "name": "Salesforce"},
        {"tenant": "qualcomm", "domain": "qualcomm.wd5.myworkdayjobs.com", "name": "Qualcomm"},
        {"tenant": "adobe", "domain": "adobe.wd5.myworkdayjobs.com", "name": "Adobe"},
        {"tenant": "walmart", "domain": "walmart.wd5.myworkdayjobs.com", "name": "Walmart"},
        {"tenant": "target", "domain": "target.wd5.myworkdayjobs.com", "name": "Target"},
        {"tenant": "nike", "domain": "nike.wd1.myworkdayjobs.com", "name": "Nike"},
        {"tenant": "nvidia", "domain": "nvidia.wd5.myworkdayjobs.com", "name": "Nvidia"},
        {"tenant": "accenture", "domain": "accenture.wd3.myworkdayjobs.com", "name": "Accenture"},
    ],

    # 2. Greenhouse Job Board API (Public & Free)
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

    # 3. Lever Postings API (Public & Free)
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

    # 4. Ashby Job Postings API (Public & Free)
    # Endpoint: https://api.ashbyhq.com/posting-api/job-board/{board}
    "ashby": [
        {"board": "linear", "name": "Linear"},
        {"board": "ramp", "name": "Ramp"},
        {"board": "notion", "name": "Notion"},
        {"board": "vercel", "name": "Vercel"},
        {"board": "zapier", "name": "Zapier"},
        {"board": "retool", "name": "Retool"},
        {"board": "cursor", "name": "Cursor"},
        {"board": "openai", "name": "OpenAI"},
        {"board": "anthropic", "name": "Anthropic"},
    ],

    # 5. SmartRecruiters Postings API
    "smartrecruiters": [
        {"company_id": "Visa", "name": "Visa"},
        {"company_id": "Skechers", "name": "Skechers"},
        {"company_id": "BoschGroup", "name": "Bosch"},
        {"company_id": "LinkedIn", "name": "LinkedIn"},
        {"company_id": "IKEA", "name": "IKEA"},
    ],

    # 6. Workable
    "workable": [
        {"subdomain": "wise", "name": "TransferWise"},
        {"subdomain": "sephora", "name": "Sephora"},
        {"subdomain": "bevi", "name": "Bevi"},
    ],

    # 7. Teamtailor
    "teamtailor": [
        {"subdomain": "danielwellington", "name": "Daniel Wellington"},
        {"subdomain": "dott", "name": "Dott"},
        {"subdomain": "kry", "name": "Kry"},
        {"subdomain": "mentimeter", "name": "Mentimeter"},
    ],

    # 8. Recruitee
    "recruitee": [
        {"subdomain": "hotjar", "name": "Hotjar"},
        {"subdomain": "transcom", "name": "Transcom"},
        {"subdomain": "usabilla", "name": "Usabilla"},
        {"subdomain": "greenpeace", "name": "Greenpeace"},
    ],

    # 9. BambooHR
    "bamboohr": [
        {"subdomain": "jane", "name": "Jane"},
        {"subdomain": "postmates", "name": "Postmates"},
        {"subdomain": "soundcloud", "name": "SoundCloud"},
    ],

    # 10. SAP SuccessFactors
    "successfactors": [
        {"company_key": "siemens", "name": "Siemens"},
        {"company_key": "bmw", "name": "BMW"},
        {"company_key": "vodafone", "name": "Vodafone"},
        {"company_key": "tata", "name": "Tata Group"},
    ],

    # 11. Oracle Taleo / Cloud HCM
    "taleo": [
        {"company_key": "oracle", "name": "Oracle"},
        {"company_key": "deloitte", "name": "Deloitte"},
        {"company_key": "boeing", "name": "Boeing"},
        {"company_key": "starbucks", "name": "Starbucks"},
    ],

    # 12. iCIMS
    "icims": [
        {"subdomain": "fedex", "name": "FedEx"},
        {"subdomain": "cvshealth", "name": "CVS Health"},
        {"subdomain": "target", "name": "Target Retail"},
    ],

    # 13. Jobvite
    "jobvite": [
        {"company_id": "blizzard", "name": "Blizzard"},
        {"company_id": "zillow", "name": "Zillow"},
        {"company_id": "ingrammicro", "name": "Ingram Micro"},
    ],

    # 14. Breezy HR
    "breezy": [
        {"subdomain": "launchdarkly", "name": "LaunchDarkly"},
    ],

    # 15. Pinpoint
    "pinpoint": [
        {"subdomain": "pinpoint", "name": "Pinpoint"},
    ],

    # 16. Personio
    "personio": [
        {"subdomain": "personio", "name": "Personio"},
    ],

    # 17. UKG (UltiPro)
    "ukg": [
        {"tenant": "firstnational", "name": "First National"},
    ],

    # 18. Cornerstone OnDemand
    "cornerstone": [
        {"portal": "westerndigital", "name": "Western Digital"},
    ]
}

def get_company_board_token(company_name: str) -> Dict[str, Any]:
    """Look up a company's known ATS provider and board token or identifier."""
    if not company_name:
        return {}
    clean_name = company_name.lower().strip()
    
    for provider, companies in COMPANY_ATS_REGISTRY.items():
        for comp in companies:
            ident = (
                comp.get("token") or comp.get("site") or comp.get("board") or
                comp.get("tenant") or comp.get("company_id") or comp.get("subdomain") or
                comp.get("company_key") or comp.get("portal") or ""
            )
            if (
                comp["name"].lower() == clean_name or
                ident.lower() == clean_name or
                comp["name"].lower() in clean_name or
                clean_name in comp["name"].lower()
            ):
                return {
                    "ats_provider": provider.capitalize() if provider != "ashby" else "Ashby",
                    "identifier": ident,
                    "name": comp["name"],
                    "domain": comp.get("domain", "")
                }
    return {}
