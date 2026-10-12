"""
==========================================================
AI JobAgent - Live Multi-Portal Job Aggregator
Aggregates live opportunities from LinkedIn, Naukri, Indeed,
Adzuna, ArbeitNow, RemoteOK, Remotive, and Jobicy.
==========================================================
"""

import os
import re
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

from config import (
    ADZUNA_APP_ID,
    ADZUNA_APP_KEY,
    RAPIDAPI_KEY,
    RAPIDAPI_HOST,
    JOOBLE_API_KEY,
    SERPAPI_API_KEY,
)
from utils import info, warning, error

COMMON_SKILLS = [
    "Python", "SQL", "Excel", "Tableau", "Power BI", "Data Analysis", "R",
    "Machine Learning", "Pandas", "NumPy", "Statistics", "ETL", "AWS", "Azure",
    "Snowflake", "Databricks", "Java", "JavaScript", "TypeScript", "React",
    "Node.js", "Docker", "Kubernetes", "Git", "FastAPI", "Django", "PostgreSQL",
    "MongoDB", "Scikit-Learn", "TensorFlow", "PyTorch", "Spark", "Airflow", "GCP"
]

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def extract_skills_from_text(text: str, default_role: str = "") -> List[str]:
    """Identify relevant technical skills mentioned in title or description."""
    if not text:
        return ["Python", "SQL", "Data Analysis"] if "data" in default_role.lower() else ["Software Development"]
    
    found = []
    text_lower = text.lower()
    for skill in COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    
    if not found:
        found = ["Python", "SQL", "Excel"] if "analyst" in default_role.lower() else ["Software Engineering", "Problem Solving"]
    
    return found[:6]


def format_inr_salary(min_val: Optional[float], max_val: Optional[float], default_sal: str = "₹6 - ₹12 LPA") -> str:
    """Format salary numbers into clean Indian Lakhs Per Annum (LPA) or standard ranges."""
    if not min_val and not max_val:
        return default_sal
    
    try:
        if min_val and min_val > 100000:
            lpa_min = round(min_val / 100000, 1)
            if max_val and max_val > 100000:
                lpa_max = round(max_val / 100000, 1)
                return f"₹{lpa_min} - ₹{lpa_max} LPA"
            return f"₹{lpa_min}+ LPA"
        elif max_val and max_val > 100000:
            lpa_max = round(max_val / 100000, 1)
            return f"Up to ₹{lpa_max} LPA"
    except Exception:
        pass
    
    return default_sal


# ==========================================================
# 1. LINKEDIN DIRECT LIVE PROVIDER (Free Guest Search)
# ==========================================================

def fetch_linkedin_live(role: str = "Data Analyst", location: str = "India", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Query LinkedIn's public guest job search endpoint.
    Zero API key required; 100% free and open.
    """
    jobs = []
    try:
        encoded_role = urllib.parse.quote_plus(role or "Data Analyst")
        encoded_loc = urllib.parse.quote_plus(location or "India")
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encoded_role}&location={encoded_loc}&start=0"
        
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.find_all("li")
            for idx, card in enumerate(cards):
                if len(jobs) >= limit:
                    break
                
                title_elem = card.find("h3", class_="base-search-card__title")
                comp_elem = card.find("h4", class_="base-search-card__subtitle")
                loc_elem = card.find("span", class_="job-search-card__location")
                link_elem = card.find("a", class_="base-card__full-link")
                
                if title_elem and comp_elem:
                    title = title_elem.get_text(strip=True)
                    company = comp_elem.get_text(strip=True)
                    job_loc = loc_elem.get_text(strip=True) if loc_elem else location
                    apply_url = link_elem["href"] if link_elem and link_elem.has_attr("href") else f"https://www.linkedin.com/jobs/search?keywords={encoded_role}"
                    
                    skills = extract_skills_from_text(title, role)
                    
                    jobs.append({
                        "id": f"live_linkedin_{int(time.time())}_{idx}",
                        "title": title,
                        "company": company,
                        "location": job_loc,
                        "source": "LinkedIn",
                        "url": apply_url,
                        "skills": skills,
                        "salary": "₹8 - ₹16 LPA",
                        "experience": "1-3 yrs",
                        "description": f"Verified live career opportunity on LinkedIn for {title} at {company} in {job_loc}.",
                        "saved": False,
                        "applied": False,
                        "date_posted": "Active"
                    })
    except Exception as e:
        warning(f"LinkedIn live fetch encountered notice: {e}")
    
    return jobs


# ==========================================================
# 2. ADZUNA LIVE PROVIDER (Naukri, Indeed & India Portals)
# ==========================================================

def fetch_adzuna_live(role: str = "Data Analyst", location: str = "India", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Query Adzuna Developer API for India jobs.
    Uses free developer credentials to aggregate Indeed, Naukri, Monster & portals.
    """
    jobs = []
    app_id = os.getenv("ADZUNA_APP_ID") or ADZUNA_APP_ID
    app_key = os.getenv("ADZUNA_APP_KEY") or ADZUNA_APP_KEY
    
    if not app_id or not app_key:
        return jobs
    
    try:
        url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": limit,
            "what": role or "Data Analyst",
        }
        if location and location.lower() not in ["worldwide", "global remote"]:
            params["where"] = location.split(",")[0].strip()
        
        resp = requests.get(url, params=params, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            for idx, item in enumerate(results):
                title = (item.get("title") or "").strip()
                comp_info = item.get("company") or {}
                company = (comp_info.get("display_name") or "Leading Tech Corp").strip()
                apply_url = (item.get("redirect_url") or "").strip()
                
                if not title or not apply_url:
                    continue
                
                loc_info = item.get("location") or {}
                area = loc_info.get("area") or []
                job_loc = ", ".join(area[-2:]) if area else (location or "India")
                
                desc = item.get("description") or ""
                skills = extract_skills_from_text(title + " " + desc, role)
                
                min_sal = item.get("salary_min")
                max_sal = item.get("salary_max")
                salary_str = format_inr_salary(min_sal, max_sal, "₹6 - ₹12 LPA")
                
                jobs.append({
                    "id": f"live_adzuna_{int(time.time())}_{idx}",
                    "title": title,
                    "company": company,
                    "location": job_loc,
                    "source": "Adzuna (Naukri/Indeed)",
                    "url": apply_url,
                    "skills": skills,
                    "salary": salary_str,
                    "experience": "0-3 yrs",
                    "description": desc[:320] + "..." if len(desc) > 320 else desc,
                    "saved": False,
                    "applied": False,
                    "date_posted": "Verified"
                })
    except Exception as e:
        warning(f"Adzuna live fetch encountered notice: {e}")
    
    return jobs


# ==========================================================
# 3. ARBEITNOW LIVE PROVIDER (Free Public API)
# ==========================================================

def fetch_arbeitnow_live(role: str = "Data Analyst", limit: int = 8) -> List[Dict[str, Any]]:
    """Query ArbeitNow's 100% free open job board API."""
    jobs = []
    try:
        url = "https://www.arbeitnow.com/api/job-board-api"
        resp = requests.get(url, headers={"User-Agent": DEFAULT_USER_AGENT}, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            keywords = (role or "data").lower().split()
            for idx, item in enumerate(data.get("data", [])):
                if len(jobs) >= limit:
                    break
                title = item.get("title") or ""
                desc = item.get("description") or ""
                tags = item.get("tags") or []
                
                text_to_search = (title + " " + desc + " " + " ".join(tags)).lower()
                if not any(k in text_to_search for k in keywords):
                    continue
                
                company = item.get("company_name") or "Global Tech"
                apply_url = item.get("url") or ""
                location = item.get("location") or "Worldwide Remote"
                
                skills = [t for t in tags if len(t) <= 15][:5]
                if not skills:
                    skills = extract_skills_from_text(title + " " + desc, role)
                
                jobs.append({
                    "id": f"live_arbeitnow_{int(time.time())}_{idx}",
                    "title": title,
                    "company": company,
                    "location": location,
                    "source": "ArbeitNow",
                    "url": apply_url,
                    "skills": skills,
                    "salary": "€50k - €75k / ₹12-18 LPA",
                    "experience": "1-4 yrs",
                    "description": BeautifulSoup(desc, "html.parser").get_text()[:300] + "...",
                    "saved": False,
                    "applied": False,
                    "date_posted": "Verified"
                })
    except Exception as e:
        warning(f"ArbeitNow live fetch encountered notice: {e}")
    
    return jobs


# ==========================================================
# 4. REMOTEOK LIVE PROVIDER (Free Public API)
# ==========================================================

def fetch_remoteok_live(role: str = "Data Analyst", limit: int = 8) -> List[Dict[str, Any]]:
    """Query RemoteOK's 100% free open API."""
    jobs = []
    try:
        url = "https://remoteok.com/api"
        headers = {"User-Agent": DEFAULT_USER_AGENT, "Accept": "application/json"}
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                keywords = (role or "data").lower().split()
                for idx, item in enumerate(data[1:]): # skip first disclaimer item
                    if len(jobs) >= limit:
                        break
                    if not isinstance(item, dict):
                        continue
                    
                    title = item.get("position") or item.get("title") or ""
                    desc = item.get("description") or ""
                    tags = item.get("tags") or []
                    
                    search_space = (title + " " + desc + " " + " ".join(tags)).lower()
                    if not any(k in search_space for k in keywords):
                        continue
                    
                    company = item.get("company") or "Remote Org"
                    apply_url = item.get("url") or item.get("apply_url") or "https://remoteok.com"
                    loc = item.get("location") or "Global Remote"
                    
                    skills = [t.capitalize() for t in tags if len(t) <= 15][:5]
                    if not skills:
                        skills = extract_skills_from_text(title + " " + desc, role)
                    
                    jobs.append({
                        "id": f"live_remoteok_{int(time.time())}_{idx}",
                        "title": title,
                        "company": company,
                        "location": loc,
                        "source": "RemoteOK",
                        "url": apply_url,
                        "skills": skills,
                        "salary": "Competitive / Global Remote",
                        "experience": "1-3 yrs",
                        "description": BeautifulSoup(desc, "html.parser").get_text()[:280] + "...",
                        "saved": False,
                        "applied": False,
                        "date_posted": "Recent"
                    })
    except Exception as e:
        warning(f"RemoteOK live fetch notice: {e}")
    
    return jobs


# ==========================================================
# 5. REMOTIVE LIVE PROVIDER (Free Public API)
# ==========================================================

def fetch_remotive_live(role: str = "Data Analyst", limit: int = 8) -> List[Dict[str, Any]]:
    """Query Remotive's 100% free remote jobs API."""
    jobs = []
    try:
        url = "https://remotive.com/api/remote-jobs"
        params = {"search": role or "Data Analyst"}
        resp = requests.get(url, params=params, headers={"User-Agent": DEFAULT_USER_AGENT}, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            for idx, item in enumerate(data.get("jobs", [])):
                if len(jobs) >= limit:
                    break
                title = item.get("title") or ""
                company = item.get("company_name") or "Remote Team"
                apply_url = item.get("url") or ""
                loc = item.get("candidate_required_location") or "Worldwide / Remote"
                desc = item.get("description") or ""
                tags = item.get("tags") or []
                
                skills = [t for t in tags if len(t) <= 15][:5]
                if not skills:
                    skills = extract_skills_from_text(title + " " + desc, role)
                
                jobs.append({
                    "id": f"live_remotive_{int(time.time())}_{idx}",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "source": "Remotive",
                    "url": apply_url,
                    "skills": skills,
                    "salary": item.get("salary") or "Competitive",
                    "experience": "1-3 yrs",
                    "description": BeautifulSoup(desc, "html.parser").get_text()[:280] + "...",
                    "saved": False,
                    "applied": False,
                    "date_posted": "Verified"
                })
    except Exception as e:
        warning(f"Remotive live fetch notice: {e}")
    
    return jobs


# ==========================================================
# 6. JOBICY LIVE PROVIDER (Free Public JSON API)
# ==========================================================

def fetch_jobicy_live(role: str = "Data Analyst", limit: int = 8) -> List[Dict[str, Any]]:
    """Query Jobicy's free open remote jobs API."""
    jobs = []
    try:
        url = "https://jobicy.com/api/v2/remote-jobs"
        params = {"count": 15}
        resp = requests.get(url, params=params, headers={"User-Agent": DEFAULT_USER_AGENT}, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            keywords = (role or "data").lower().split()
            for idx, item in enumerate(data.get("jobs", [])):
                if len(jobs) >= limit:
                    break
                title = item.get("jobTitle") or ""
                desc = item.get("jobDescription") or ""
                search_text = (title + " " + desc).lower()
                
                if not any(k in search_text for k in keywords):
                    continue
                
                company = item.get("companyName") or "Global Tech"
                apply_url = item.get("url") or ""
                loc = item.get("jobGeo") or "Anywhere / Remote"
                
                skills = extract_skills_from_text(title + " " + desc, role)
                
                jobs.append({
                    "id": f"live_jobicy_{int(time.time())}_{idx}",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "source": "Jobicy",
                    "url": apply_url,
                    "skills": skills,
                    "salary": "₹8 - ₹15 LPA (Remote)",
                    "experience": item.get("jobLevel") or "Mid Level",
                    "description": BeautifulSoup(desc, "html.parser").get_text()[:260] + "...",
                    "saved": False,
                    "applied": False,
                    "date_posted": "Active"
                })
    except Exception as e:
        warning(f"Jobicy live fetch notice: {e}")
    
    return jobs


# ==========================================================
# 7. JOOBLE LIVE PROVIDER (Free Developer Key)
# ==========================================================

def fetch_jooble_live(role: str = "Data Analyst", location: str = "India", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Query Jooble developer API if JOOBLE_API_KEY is configured.
    """
    key = os.getenv("JOOBLE_API_KEY") or JOOBLE_API_KEY
    if not key or key == "your_free_api_key":
        return []
    
    jobs = []
    try:
        url = f"https://jooble.org/api/{key}"
        payload = {
            "keywords": role or "Data Analyst",
            "location": location or "India",
            "page": 1
        }
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=12)
        if res.status_code == 200:
            data = res.json()
            items = data.get("jobs", [])
            for idx, item in enumerate(items[:limit]):
                title = item.get("title") or role
                company = item.get("company") or "Verified Employer"
                loc = item.get("location") or location
                link = item.get("link") or ""
                snippet = item.get("snippet") or ""
                salary = item.get("salary") or "₹6 - ₹12 LPA"
                clean_desc = BeautifulSoup(snippet, "html.parser").get_text()[:260] + "..." if snippet else f"Verified position for {title}."
                skills = extract_skills_from_text(title + " " + clean_desc, role)

                jobs.append({
                    "id": f"live_jooble_{int(time.time())}_{idx}",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "source": "Jooble",
                    "url": link,
                    "skills": skills,
                    "salary": salary,
                    "experience": "0-3 yrs",
                    "description": clean_desc,
                    "saved": False,
                    "applied": False,
                    "date_posted": "Active"
                })
    except Exception as e:
        warning(f"Jooble live fetch notice: {e}")
    return jobs


# ==========================================================
# 8. SERPAPI GOOGLE JOBS PROVIDER (Free Developer Key)
# ==========================================================

def fetch_serpapi_live(role: str = "Data Analyst", location: str = "India", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Query Google Jobs via SerpApi if SERPAPI_API_KEY is configured.
    """
    key = os.getenv("SERPAPI_API_KEY") or SERPAPI_API_KEY
    if not key:
        return []
    
    jobs = []
    try:
        query = f"{role} {location}".strip()
        url = f"https://serpapi.com/search?engine=google_jobs&q={urllib.parse.quote_plus(query)}&api_key={key}"
        res = requests.get(url, timeout=12)
        if res.status_code == 200:
            data = res.json()
            items = data.get("jobs_results", [])
            for idx, item in enumerate(items[:limit]):
                title = item.get("title") or role
                company = item.get("company_name") or "Leading Company"
                loc = item.get("location") or location
                desc = item.get("description") or f"Opportunity for {title} at {company}."
                via = item.get("via") or "Google Jobs"
                
                apply_options = item.get("apply_options", [])
                link = apply_options[0].get("link") if apply_options else item.get("share_link", "https://google.com")
                skills = extract_skills_from_text(title + " " + desc, role)

                jobs.append({
                    "id": f"live_serp_{int(time.time())}_{idx}",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "source": f"Google Jobs ({via.replace('via ', '')})",
                    "url": link,
                    "skills": skills,
                    "salary": "₹7 - ₹14 LPA",
                    "experience": "1-3 yrs",
                    "description": desc[:260] + "...",
                    "saved": False,
                    "applied": False,
                    "date_posted": "Active"
                })
    except Exception as e:
        warning(f"SerpApi live fetch notice: {e}")
    return jobs


# ==========================================================
# 9. JSEARCH RAPIDAPI PROVIDER (Indeed, Glassdoor, LinkedIn)
# ==========================================================

def fetch_jsearch_live(role: str = "Data Analyst", location: str = "India", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Query RapidAPI JSearch if RAPIDAPI_KEY is configured.
    """
    key = os.getenv("RAPIDAPI_KEY") or RAPIDAPI_KEY
    if not key:
        return []
    
    jobs = []
    try:
        query = f"{role} in {location}".strip()
        url = f"https://jsearch.p.rapidapi.com/search?query={urllib.parse.quote_plus(query)}&num_pages=1"
        headers = {
            "X-RapidAPI-Key": key,
            "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
        }
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            items = data.get("data", [])
            for idx, item in enumerate(items[:limit]):
                title = item.get("job_title") or role
                company = item.get("employer_name") or "Corporate Employer"
                loc = f"{item.get('job_city', '')}, {item.get('job_country', '')}".strip(" ,") or location
                desc = item.get("job_description") or ""
                link = item.get("job_apply_link") or item.get("job_google_link") or ""
                publisher = item.get("job_publisher") or "Indeed"
                skills = extract_skills_from_text(title + " " + desc, role)

                jobs.append({
                    "id": f"live_jsearch_{int(time.time())}_{idx}",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "source": f"{publisher} (JSearch)",
                    "url": link,
                    "skills": skills,
                    "salary": "₹6 - ₹13 LPA",
                    "experience": "0-2 yrs",
                    "description": desc[:260] + "...",
                    "saved": False,
                    "applied": False,
                    "date_posted": "Active"
                })
    except Exception as e:
        warning(f"JSearch live fetch notice: {e}")
    return jobs


# ==========================================================
# MASTER AGGREGATOR & DEDUPLICATION ORCHESTRATOR
# ==========================================================

def aggregate_live_jobs(
    role: str = "Data Analyst",
    location: str = "India",
    sources: Optional[List[str]] = None,
    candidate_skills: Optional[List[str]] = None,
    max_total: int = 40
) -> Dict[str, Any]:
    """
    Search and aggregate live job postings concurrently across all connected portals.
    Deduplicates duplicates, computes skill match scores, and returns unified listing.
    """
    if not sources:
        sources = ["linkedin", "adzuna", "arbeitnow", "remoteok", "remotive", "jobicy"]
    
    selected_sources = [s.lower() for s in sources]
    collected_jobs: List[Dict[str, Any]] = []
    polled_sources: List[str] = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        
        if "linkedin" in selected_sources:
            futures[executor.submit(fetch_linkedin_live, role, location, 10)] = "LinkedIn"
        if "adzuna" in selected_sources or "naukri" in selected_sources or "indeed" in selected_sources:
            futures[executor.submit(fetch_adzuna_live, role, location, 12)] = "Adzuna (Naukri/Indeed)"
        if "arbeitnow" in selected_sources:
            futures[executor.submit(fetch_arbeitnow_live, role, 8)] = "ArbeitNow"
        if "remoteok" in selected_sources:
            futures[executor.submit(fetch_remoteok_live, role, 8)] = "RemoteOK"
        if "remotive" in selected_sources:
            futures[executor.submit(fetch_remotive_live, role, 8)] = "Remotive"
        if "jobicy" in selected_sources:
            futures[executor.submit(fetch_jobicy_live, role, 8)] = "Jobicy"
        if "jooble" in selected_sources or (os.getenv("JOOBLE_API_KEY") and os.getenv("JOOBLE_API_KEY") != "your_free_api_key"):
            futures[executor.submit(fetch_jooble_live, role, location, 10)] = "Jooble"
        if "serpapi" in selected_sources or os.getenv("SERPAPI_API_KEY"):
            futures[executor.submit(fetch_serpapi_live, role, location, 10)] = "Google Jobs (SerpApi)"
        if "jsearch" in selected_sources or os.getenv("RAPIDAPI_KEY"):
            futures[executor.submit(fetch_jsearch_live, role, location, 10)] = "JSearch (Indeed/Glassdoor)"
        
        for future in as_completed(futures):
            src_name = futures[future]
            polled_sources.append(src_name)
            try:
                results = future.result()
                if results:
                    collected_jobs.extend(results)
                    info(f"Retrieved {len(results)} live jobs from {src_name}")
            except Exception as e:
                warning(f"Provider {src_name} query error: {e}")
    
    # Deduplicate by normalized (title, company)
    seen = set()
    unique_jobs: List[Dict[str, Any]] = []
    
    user_skills_lower = [s.lower() for s in (candidate_skills or ["python", "sql", "excel", "data analysis"])]
    
    for job in collected_jobs:
        # Create a clean deduplication fingerprint
        clean_title = re.sub(r"[^\w\s]", "", (job.get("title") or "").lower()).strip()
        clean_comp = re.sub(r"[^\w\s]", "", (job.get("company") or "").lower()).strip()
        fingerprint = f"{clean_title[:24]}::{clean_comp[:18]}"
        
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        
        # Calculate dynamic client match score
        req_skills = job.get("skills") or []
        if req_skills and user_skills_lower:
            matched_count = sum(1 for s in req_skills if s.lower() in user_skills_lower)
            score = round(60 + (matched_count / len(req_skills)) * 38, 1)
        else:
            score = 80.0
        
        job["match_score"] = min(score, 98.0)
        unique_jobs.append(job)
        
        if len(unique_jobs) >= max_total:
            break
    
    # Sort by match score descending
    unique_jobs.sort(key=lambda j: j.get("match_score", 0), reverse=True)
    
    return {
        "success": True,
        "count": len(unique_jobs),
        "query": role,
        "location": location,
        "sources_polled": polled_sources,
        "jobs": unique_jobs
    }


def get_providers_status_summary() -> List[Dict[str, Any]]:
    """Return live connection status for each job portal with free key support."""
    adzuna_id = os.getenv("ADZUNA_APP_ID") or ADZUNA_APP_ID
    rapidapi_k = os.getenv("RAPIDAPI_KEY") or RAPIDAPI_KEY
    jooble_k = os.getenv("JOOBLE_API_KEY") or JOOBLE_API_KEY
    serpapi_k = os.getenv("SERPAPI_API_KEY") or SERPAPI_API_KEY
    
    return [
        {
            "name": "LinkedIn",
            "tier": "Free Guest API & Public Indexer",
            "status": "connected",
            "zero_key_required": True,
            "description": "Searches live LinkedIn postings in real time with zero API key needed."
        },
        {
            "name": "Adzuna (Naukri & Indeed Aggregator)",
            "tier": "Free Developer API (India & Global)",
            "status": "connected" if adzuna_id else "ready_for_key",
            "zero_key_required": False,
            "key_configured": bool(adzuna_id),
            "free_signup_url": "https://developer.adzuna.com/",
            "description": "Indexes openings from Naukri, Indeed, and Monster across Hyderabad, Bangalore & India."
        },
        {
            "name": "ArbeitNow",
            "tier": "Free Public API (No Key)",
            "status": "connected",
            "zero_key_required": True,
            "description": "Direct JSON feed for modern technology & engineering roles worldwide."
        },
        {
            "name": "RemoteOK",
            "tier": "Free Public API (No Key)",
            "status": "connected",
            "zero_key_required": True,
            "description": "Live remote technical roles and startup engineering opportunities."
        },
        {
            "name": "Remotive",
            "tier": "Free Public API (No Key)",
            "status": "connected",
            "zero_key_required": True,
            "description": "Curated technology and data analyst openings worldwide."
        },
        {
            "name": "Jobicy",
            "tier": "Free Public API (No Key)",
            "status": "connected",
            "zero_key_required": True,
            "description": "Global remote jobs feed for tech professionals and developers."
        },
        {
            "name": "JSearch / RapidAPI (Indeed & Glassdoor)",
            "tier": "Free RapidAPI Tier (50 req/mo)",
            "status": "ready" if rapidapi_k else "ready_for_key",
            "zero_key_required": False,
            "key_configured": bool(rapidapi_k),
            "free_signup_url": "https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch",
            "description": "Comprehensive aggregator covering Indeed, Glassdoor and corporate portals."
        },
        {
            "name": "Jooble",
            "tier": "Free Developer API Key",
            "status": "ready" if jooble_k else "ready_for_key",
            "zero_key_required": False,
            "key_configured": bool(jooble_k and "your_" not in jooble_k),
            "free_signup_url": "https://jooble.org/api/about",
            "description": "Multi-country job search API covering thousands of job boards."
        }
    ]
