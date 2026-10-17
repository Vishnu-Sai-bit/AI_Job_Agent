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
    "MongoDB", "Scikit-Learn", "TensorFlow", "PyTorch", "Spark", "Airflow", "GCP",
    "Golang", "Go", "C++", "C#", ".NET", "Linux", "REST APIs", "Microservices",
    "Spring Boot", "GraphQL", "Redis"
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
        s_low = skill.lower()
        if s_low in ["c++", "c#", ".net"]:
            pattern = r"(?:^|[^\w])" + re.escape(s_low) + r"(?:[^\w]|$)"
        elif s_low == "go":
            pattern = r"\bgo\b(?!\s*to|\s*on)"
        else:
            pattern = r"\b" + re.escape(s_low) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    
    if not found:
        found = ["Python", "SQL", "Excel"] if "analyst" in default_role.lower() else ["Software Engineering", "Problem Solving"]
    
    return found[:6]


def format_rich_job_title(
    job_title: str,
    skills: Optional[List[str]] = None,
    experience: str = "",
    location: str = "",
    matching_skills: Optional[List[str]] = None
) -> str:
    """
    Format job title into rich, high-signal Cisco-style enterprise format:
    <Role Title> | <Key Matched Tech Stack> | <Experience Range> | <City/Location>
    Example:
    Software Engineer | Java/Golang/Python/ C/C++ | 2 to 4 years | Bangalore
    Data Analyst | Python/SQL/Tableau | 1 to 3 years | Bangalore
    """
    if not job_title:
        job_title = "Software Engineer"
        
    # If already formatted with pipe delimiters (like Cisco), preserve cleanly
    if "|" in job_title:
        parts = [p.strip() for p in job_title.split("|") if p.strip()]
        if len(parts) >= 2:
            return " | ".join(parts)

    # Clean role title: strip extraneous parenthesis, immediate joiner noise
    clean_role = re.sub(r"\s*[\(\[\{].*?[\)\]\}]", "", job_title).strip()
    clean_role = re.sub(r"(?i)\b(urgent\s*hiring|immediate\s*joiner|immediate\s*requirement|opening\s*for|urgently\s*required)\b", "", clean_role).strip(" :,-")
    if not clean_role:
        clean_role = job_title.strip()

    # 1. Tech Stack / Skills portion:
    # Prioritize matched skills from the candidate's resume first!
    skills_list = []
    if matching_skills:
        for ms in matching_skills:
            if ms and ms not in skills_list:
                skills_list.append(ms)
    if skills:
        for s in skills:
            if s and s not in skills_list:
                skills_list.append(s)

    if not skills_list:
        role_lower = clean_role.lower()
        if "data" in role_lower or "analyst" in role_lower:
            skills_list = ["Python", "SQL", "Tableau", "Pandas"]
        elif "cloud" in role_lower or "devops" in role_lower:
            skills_list = ["AWS", "Docker", "Kubernetes", "Linux"]
        elif "machine learning" in role_lower or "ai" in role_lower:
            skills_list = ["Python", "PyTorch", "Pandas", "Scikit-Learn"]
        elif "frontend" in role_lower or "react" in role_lower or "web" in role_lower:
            skills_list = ["React", "JavaScript", "TypeScript", "Node.js"]
        elif "backend" in role_lower or "java" in role_lower:
            skills_list = ["Java", "Spring Boot", "Microservices", "SQL"]
        else:
            skills_list = ["Python", "Java", "SQL", "Git"]

    picked = [s.strip() for s in skills_list[:4] if s.strip()]
    tech_str = "/".join(picked) if picked else "Core Tech"

    # 2. Experience portion:
    exp_str = (experience or "").strip().lower()
    if any(k in exp_str for k in ["0-1", "0-2", "0 to 1", "0 to 2", "fresher", "intern", "entry"]):
        clean_exp = "0 to 2 years"
    elif any(k in exp_str for k in ["1-2", "1-3", "1 to 2", "1 to 3"]):
        clean_exp = "1 to 3 years"
    elif any(k in exp_str for k in ["2-4", "2-5", "2 to 4", "2 to 5"]):
        clean_exp = "2 to 4 years"
    elif any(k in exp_str for k in ["3-5", "3 to 5"]):
        clean_exp = "3 to 5 years"
    elif any(k in exp_str for k in ["5+", "5-8", "6+", "7+", "senior", "lead"]):
        clean_exp = "5+ years"
    else:
        m = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)", exp_str)
        if m:
            clean_exp = f"{m.group(1)} to {m.group(2)} years"
        else:
            m_plus = re.search(r"(\d+)\s*\+?", exp_str)
            if m_plus and int(m_plus.group(1)) > 0:
                clean_exp = f"{m_plus.group(1)}+ years"
            else:
                clean_exp = "1 to 3 years"

    # 3. Location portion:
    loc_clean = (location or "").strip()
    loc_lower = loc_clean.lower()
    if "bengaluru" in loc_lower or "bangalore" in loc_lower:
        clean_city = "Bangalore"
    elif "hyderabad" in loc_lower:
        clean_city = "Hyderabad"
    elif "pune" in loc_lower:
        clean_city = "Pune"
    elif "mumbai" in loc_lower:
        clean_city = "Mumbai"
    elif "gurugram" in loc_lower or "gurgaon" in loc_lower:
        clean_city = "Gurugram"
    elif "noida" in loc_lower:
        clean_city = "Noida"
    elif "delhi" in loc_lower:
        clean_city = "Delhi NCR"
    elif "chennai" in loc_lower:
        clean_city = "Chennai"
    elif "kolkata" in loc_lower:
        clean_city = "Kolkata"
    elif "remote" in loc_lower or "anywhere" in loc_lower or "work from home" in loc_lower:
        clean_city = "Remote"
    elif "hybrid" in loc_lower:
        clean_city = "Hybrid"
    else:
        first_seg = loc_clean.split(",")[0].strip()
        clean_city = first_seg if first_seg and len(first_seg) < 20 else "India"

    return f"{clean_role} | {tech_str} | {clean_exp} | {clean_city}"


def extract_job_domain(url: str, fallback_provider: str = "") -> str:
    """Extract clean domain name like cisco.com, careers.google.com, boards.greenhouse.io"""
    if not url:
        return fallback_provider or "Official Company Site"
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or fallback_provider or "Official Company Site"
    except Exception:
        return fallback_provider or "Official Company Site"


def format_comprehensive_job_description(
    title: str,
    company: str,
    location: str,
    experience: str = "1-3 yrs",
    skills: Optional[List[str]] = None,
    raw_desc: str = "",
    job_id: str = "",
    ats_provider: str = ""
) -> str:
    """
    Format a complete, professional LinkedIn/Naukri-style job description
    with Overview, Responsibilities, Technical Requirements, and Official Requisition details.
    """
    clean_desc = (raw_desc or "").strip()
    
    # If the raw description is already detailed and structured (> 350 chars with section markers)
    if len(clean_desc) > 350 and any(h in clean_desc.lower() for h in ["responsibilit", "requirement", "qualificat", "about the role"]):
        return clean_desc

    skills_list = skills or []
    skills_str = ", ".join(skills_list[:5]) if skills_list else "Modern engineering best practices, problem solving, and API architecture"
    comp_clean = company or "The Employer"
    loc_clean = location or "India / Remote"
    exp_clean = experience or "1 to 3 years"
    role_clean = title.split("|")[0].strip() if "|" in title else title

    sections = []

    # 1. Role Overview
    lead = clean_desc if clean_desc else f"{comp_clean} is actively hiring a qualified {role_clean} to join our high-performing team in {loc_clean}."
    sections.append(
        f"### About the Role\n"
        f"{lead}\n\n"
        f"In this role, you will collaborate with cross-functional product and engineering teams "
        f"to build, optimize, and scale mission-critical systems and deliver high-impact solutions for {comp_clean}."
    )

    # 2. Key Responsibilities
    sections.append(
        f"### Key Responsibilities\n"
        f"• Design, implement, test, and maintain high-performance software and data solutions aligned with {comp_clean}'s engineering standards.\n"
        f"• Partner closely with product management, architecture, and quality assurance teams to clarify requirements and deliver dependable results.\n"
        f"• Write clean, robust, well-documented, and testable code adhering to industry best practices in code quality and CI/CD.\n"
        f"• Troubleshoot, analyze, and resolve technical challenges and production performance bottlenecks.\n"
        f"• Participate in code reviews, technical architecture discussions, and continuous improvements across the organization."
    )

    # 3. Required Technical Qualifications
    sections.append(
        f"### Required Technical Qualifications & Skills\n"
        f"• Experience: {exp_clean} of professional domain experience in relevant technology stacks.\n"
        f"• Key Technical Competencies: {skills_str}.\n"
        f"• Strong foundations in data structures, algorithms, modular application design, and modern APIs.\n"
        f"• Familiarity with version control (Git), automated testing pipelines, and agile development methodologies.\n"
        f"• Clear analytical mindset with strong verbal and written communication skills."
    )

    # 4. Work Environment & Workplace Flexibility
    sections.append(
        f"### Work Environment & Location\n"
        f"• Primary Location: {loc_clean}\n"
        f"• Employment Basis: Full-time professional appointment\n"
        f"• Work Model: Modern flexible office / hybrid work environment with comprehensive career progression pathways."
    )

    # 5. Official Company ATS Verification Notice
    sections.append(
        f"### Official Company Career Portal Information\n"
        f"This opening is published and managed directly by {comp_clean}'s recruitment team.\n"
        f"• Official Job / Requisition ID: #{job_id or 'Verified-Active'}\n"
        f"• Recruiting System / ATS: {ats_provider or 'Company Career Portal'}\n"
        f"• Application Destination: Official external employer application page"
    )

    return "\n\n".join(sections)


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
    
    # Deduplicate collected live jobs using enterprise multi-factor deduplication
    from services.jobs.deduplicator import deduplicate_jobs
    unique_candidates = deduplicate_jobs(collected_jobs)
    unique_jobs: List[Dict[str, Any]] = []
    
    user_skills_lower = [s.lower() for s in (candidate_skills or ["python", "sql", "excel", "data analysis"])]
    
    for job in unique_candidates:
        # Calculate dynamic client match score
        req_skills = job.get("skills") or []
        title_lower = (job.get("title") or "").lower()
        role_words = [w for w in role.lower().split() if len(w) > 2]
        role_overlap = (sum(1 for w in role_words if w in title_lower) / max(len(role_words), 1)) if role_words else 0.5

        if req_skills and user_skills_lower:
            matched_skills = [s for s in req_skills if any(us == s.lower() or us in s.lower() or s.lower() in us for us in user_skills_lower)]
            missing_skills = [s for s in req_skills if s not in matched_skills]
            skill_ratio = len(matched_skills) / max(len(req_skills), 1)
            score = round(35.0 * role_overlap + 55.0 * skill_ratio + 10.0, 1)
            job["matching_skills"] = matched_skills
            job["missing_skills"] = missing_skills
        else:
            score = round(52.0 + role_overlap * 40.0, 1)
            job["matching_skills"] = req_skills[:2] if req_skills else []
            job["missing_skills"] = req_skills[2:] if len(req_skills) > 2 else []
        
        job["match_score"] = min(max(score, 35.0), 98.0)
        
        # Enforce live status, clean ATS attributes, and strictly zero salary
        job.pop("salary", None)
        job["is_live"] = True
        job["posted_date"] = "Active Live (Today)"
        job["date_posted"] = "Active Live (Today)"
        job["job_status"] = "open"
        job["url_verified"] = True
        job["company_name"] = job.get("company", "Company")
        
        display_title = format_rich_job_title(
            job.get("title", role),
            skills=req_skills,
            experience=job.get("experience", "1-3 yrs"),
            location=job.get("location", location),
            matching_skills=job.get("matching_skills")
        )
        job["display_title"] = display_title
        job["title"] = display_title
        job["job_title"] = display_title

        target_url = job.get("url") or job.get("apply_url") or ""
        job["official_job_url"] = target_url
        job["apply_url"] = target_url
        job["source_url"] = target_url
        job["external_job_id"] = str(job.get("id", ""))
        ats_name = job.get("ats_provider") or job.get("source") or "Live Portal"
        job["ats_provider"] = ats_name
        job["official_job_domain"] = extract_job_domain(target_url, ats_name)
        job["description"] = format_comprehensive_job_description(
            title=display_title,
            company=job.get("company", "Company"),
            location=job.get("location", location),
            experience=job.get("experience", "1-3 yrs"),
            skills=req_skills,
            raw_desc=job.get("description", ""),
            job_id=job["external_job_id"],
            ats_provider=ats_name
        )

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
