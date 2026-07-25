"""
==========================================================
AI JobAgent - Job Search Service
Author : Beere Vishnu Sai
==========================================================
"""

from typing import List, Dict, Any
import time

from config import (
    ENABLE_REMOTIVE,
    ENABLE_REMOTEOK,
    ENABLE_ARBEITNOW,
    ENABLE_JSEARCH,
    ENABLE_THEMUSE,
    ENABLE_ADZUNA,
    ENABLE_JOOBLE,
    ENABLE_SERPAPI,
    MIN_MATCH_SCORE,
)

from models import (
    ResumeData,
    JobData,
    SearchResult,
)

from utils import (
    info,
    warning,
    exception,
    remove_duplicates,
)

from exceptions import (
    JobSearchError,
)

from services.job_matcher import (
    match_jobs,
)

# ==========================================================
# Fetch Jobs From Providers
# ==========================================================

def fetch_jobs(role: str) -> tuple[List[JobData], List[str]]:
    """
    Collect jobs from all enabled providers and return (jobs, failed_providers).
    """
    from providers.remotive import search_remotive_jobs
    from providers.remoteok import search_remoteok_jobs
    from providers.arbeitnow import search_arbeitnow_jobs
    from providers.jsearch import search_jsearch_jobs
    from providers.themuse import search_themuse_jobs
    from providers.adzuna import search_adzuna_jobs
    from providers.jooble import search_jooble_jobs
    from providers.serpapi import search_serpapi_jobs
    from providers.linkedin import search_linkedin_jobs
    from providers.naukri import search_naukri_jobs
    from providers.indeed import search_indeed_jobs
    from providers.foundit import search_foundit_jobs
    from providers.greenhouse import search_greenhouse_jobs
    from providers.lever import search_lever_jobs

    jobs: List[JobData] = []
    failed_providers: List[str] = []

    info("Starting job collection...")

    # Load provider options from config dynamically
    from config import (
        ENABLE_LINKEDIN,
        ENABLE_NAUKRI,
        ENABLE_FOUNDIT,
        ENABLE_INDEED,
        ENABLE_GREENHOUSE,
        ENABLE_LEVER,
    )

    providers_to_fetch = [
        ("Remotive", ENABLE_REMOTIVE, search_remotive_jobs),
        ("RemoteOK", ENABLE_REMOTEOK, search_remoteok_jobs),
        ("ArbeitNow", ENABLE_ARBEITNOW, search_arbeitnow_jobs),
        ("JSearch", ENABLE_JSEARCH, search_jsearch_jobs),
        ("TheMuse", ENABLE_THEMUSE, search_themuse_jobs),
        ("Adzuna", ENABLE_ADZUNA, search_adzuna_jobs),
        ("Jooble", ENABLE_JOOBLE, search_jooble_jobs),
        ("SerpApi", ENABLE_SERPAPI, search_serpapi_jobs),
        ("LinkedIn", ENABLE_LINKEDIN, search_linkedin_jobs),
        ("Naukri", ENABLE_NAUKRI, search_naukri_jobs),
        ("Indeed", ENABLE_INDEED, search_indeed_jobs),
        ("Foundit", ENABLE_FOUNDIT, search_foundit_jobs),
        ("Greenhouse", ENABLE_GREENHOUSE, search_greenhouse_jobs),
        ("Lever", ENABLE_LEVER, search_lever_jobs),
    ]

    for name, enabled, search_fn in providers_to_fetch:
        if enabled:
            try:
                info(f"Fetching {name} jobs...")
                res = search_fn(role)
                if res is not None:
                    jobs.extend(res)
                else:
                    failed_providers.append(name)
            except Exception as e:
                failed_providers.append(name)
                warning(f"{name} failed: {e}")

    info(f"Collected {len(jobs)} jobs. Failed providers: {failed_providers}")

    return jobs, failed_providers

# ==========================================================
# Clean Jobs
# ==========================================================

def clean_jobs(
    jobs: List[JobData],
) -> List[JobData]:
    """
    Remove duplicate jobs.
    """

    info("Removing duplicate jobs...")

    jobs = remove_duplicates(jobs)

    info(
        f"{len(jobs)} unique jobs remaining."
    )

    return jobs

def is_india_or_remote_job(job_loc: str) -> bool:
    """
    Check if a job is in India or remote.
    """
    if not job_loc:
        return True # Keep if location is empty (safe fallback)
    
    loc_lower = job_loc.lower()
    
    # Exclude known foreign countries/cities and worldwide
    foreign_countries = [
        "worldwide", "usa", "united states", "canada", "germany", "brazil", "europe", 
        "uk", "united kingdom", "australia", "netherlands", "france", 
        "singapore", "japan", "berlin", "munich", "toronto", "quebec",
        "london", "new york", "san francisco", "paris"
    ]
    for country in foreign_countries:
        if country in loc_lower:
            return False
            
    return True

# ==========================================================
# Search Jobs
# ==========================================================

def search_jobs(
    resume: ResumeData,
) -> SearchResult:
    """
    Search jobs from all enabled providers,
    match them with the resume,
    and return a SearchResult.
    """

    info("Starting job search...")

    start_time = time.perf_counter()

    try:
        # --------------------------------------------------
        # Fetch Jobs (Using skills as search keywords)
        # --------------------------------------------------
        # Construct search query from skills, focusing on core technical keywords first
        core_tech_keywords = {
            "python", "sql", "tableau", "power bi", "powerbi", "excel", "pandas", "numpy", 
            "r", "matlab", "scikit-learn", "tensorflow", "pytorch", "keras", "git", "docker", 
            "aws", "azure", "gcp", "fastapi", "flask", "django", "spark", "hadoop", "hive", 
            "mysql", "postgresql", "oracle", "snowflake", "dbt", "powerpoint", "sas"
        }
        tech_skills = []
        for s in (resume.skills or []):
            s_lower = s.lower().strip()
            if any(tk in s_lower for tk in core_tech_keywords):
                tech_skills.append(s)
                
        if not tech_skills:
            generic_words = {"data", "analyst", "analytics", "analysis", "system", "systems", "business", "science"}
            tech_skills = [s for s in (resume.skills or []) if s.lower().strip() not in generic_words]
            
        # 1. Fetch using preferred role (first preference)
        primary_query = resume.preferred_role or "Data Analyst"
        info(f"Fetching primary role jobs using: {primary_query}")
        jobs1, failed1 = fetch_jobs(primary_query)
        
        # 2. Fetch using boolean combination of top technical skills (second preference)
        jobs2 = []
        failed2 = []
        if tech_skills:
            secondary_query = " OR ".join(tech_skills[:4])
            info(f"Fetching secondary skills jobs using: {secondary_query}")
            jobs2, failed2 = fetch_jobs(secondary_query)
                
        # Combine results
        jobs = jobs1 + jobs2
        failed_providers = list(set(failed1 + failed2))

        # --------------------------------------------------
        # Remove Duplicates
        # --------------------------------------------------
        jobs = clean_jobs(jobs)

        # --------------------------------------------------
        # Filter for India/Remote Only
        # --------------------------------------------------
        jobs = [j for j in jobs if is_india_or_remote_job(j.location)]

        location = resume.preferred_location or resume.location

        # --------------------------------------------------
        # No Jobs Found
        # --------------------------------------------------
        if not jobs:
            warning("No jobs found.")
            return SearchResult(
                status="failed",
                message="No jobs found from providers.",
                role=resume.preferred_role,
                location=location,
                total_jobs_found=0,
                total_jobs_returned=0,
                providers_used=[],
                failed_providers=failed_providers,
                jobs=[],
            )

        # --------------------------------------------------
        # Match Jobs
        # --------------------------------------------------
        all_matched_jobs = match_jobs(
            resume,
            jobs,
        )

        # --------------------------------------------------
        # Filter by Match Score (Disabled to return all skill matches)
        # --------------------------------------------------
        good_matches = all_matched_jobs
        message = "Jobs retrieved successfully."

        # --------------------------------------------------
        # Sort Jobs
        # --------------------------------------------------
        good_matches = sort_jobs(
            good_matches,
        )

        # --------------------------------------------------
        # Providers Used
        # --------------------------------------------------
        providers = sorted(
            {
                job.provider
                for job in jobs
                if job.provider
            }
        )

        # --------------------------------------------------
        # No Matching Jobs
        # --------------------------------------------------
        if not good_matches:
            warning("No matching jobs found.")
            elapsed_time = round(
                time.perf_counter() - start_time,
                2,
            )
            
            # Check if all enabled providers failed (likely network connection failure)
            enabled_count = 0
            from config import ENABLE_REMOTIVE, ENABLE_REMOTEOK, ENABLE_ARBEITNOW, ENABLE_JSEARCH, ENABLE_THEMUSE, ENABLE_ADZUNA, ENABLE_JOOBLE, ENABLE_SERPAPI
            for enabled in [ENABLE_REMOTIVE, ENABLE_REMOTEOK, ENABLE_ARBEITNOW, ENABLE_JSEARCH, ENABLE_THEMUSE, ENABLE_ADZUNA, ENABLE_JOOBLE, ENABLE_SERPAPI]:
                if enabled:
                    enabled_count += 1
                    
            if len(failed_providers) >= enabled_count and enabled_count > 0:
                err_message = "Network Connection Error: Unable to reach job search APIs. Please check your internet connection."
            else:
                err_message = "No matching jobs found."

            return SearchResult(
                status="failed",
                message=err_message,
                role=resume.preferred_role,
                location=location,
                total_jobs_found=len(jobs),
                total_jobs_returned=0,
                search_time=elapsed_time,
                providers_used=providers,
                failed_providers=failed_providers,
                jobs=[],
            )

        # --------------------------------------------------
        # Success
        # --------------------------------------------------
        elapsed_time = round(
            time.perf_counter() - start_time,
            2,
        )

        # Calculate Auto-Learning recommendation path
        missing_skill_counts = {}
        for job in good_matches:
            for skill in job.missing_skills:
                missing_skill_counts[skill] = missing_skill_counts.get(skill, 0) + 1

        sorted_missing = sorted(missing_skill_counts.items(), key=lambda x: x[1], reverse=True)
        learning_path = []
        for skill, count in sorted_missing[:5]:
            demand_pct = round((count / len(good_matches)) * 100, 1) if good_matches else 0.0
            learning_path.append({
                "skill": skill,
                "frequency": count,
                "demand_percentage": demand_pct,
                "recommendation": f"Learn {skill} first (Required by {demand_pct}% of matching jobs)"
            })

        # Group jobs by city
        grouped_jobs = {}
        from services.location_parser import is_remote, CITY_ALIASES
        from config import DEFAULT_LOCATIONS
        
        for job in good_matches:
            loc_lower = (job.location or "").lower()
            
            # Try to identify specific city
            city_found = None
            for city in DEFAULT_LOCATIONS:
                if city.lower() in loc_lower:
                    city_found = city
                    break
                    
            # If location field is generic (like "India" or empty), scan description/title
            if not city_found:
                search_text = ((job.location or "") + " " + (job.title or "") + " " + (job.description or "")).lower()
                for city in DEFAULT_LOCATIONS:
                    city_key = city.lower()
                    if city_key in search_text:
                        city_found = city
                        break
                    # Check aliases (e.g. if "bangalore" is in text, group under "Bengaluru")
                    for alias, canonical in CITY_ALIASES.items():
                        if canonical.lower() == city_key and alias in search_text:
                            city_found = city
                            break
                            
            if job.remote or is_remote(job.location or ""):
                group_name = "Remote"
            elif city_found:
                group_name = city_found
            elif job.city:
                group_name = job.city.title()
            elif job.location:
                parts = [p.strip() for p in job.location.split(",")]
                group_name = parts[0].title() if parts else "Other India Locations"
            else:
                group_name = "Other India Locations"
                
            if group_name not in grouped_jobs:
                grouped_jobs[group_name] = []
            grouped_jobs[group_name].append(job.to_dict() if hasattr(job, "to_dict") else job)

        # Save Matched Jobs report to matched_jobs.md in workspace root
        try:
            report_lines = [
                "# 💼 Matched Jobs Report",
                f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"Preferred Role: **{resume.preferred_role}**",
                f"Candidate: **{resume.name or 'Candidate'}**",
                "",
                "| # | Job Title | Company | Location | Match Score | Apply Link |",
                "|---|---|---|---|---|---|",
            ]
            for idx, job in enumerate(good_matches):
                apply_text = f"[Apply Here]({job.apply_url})" if job.apply_url else "Not Available"
                title_clean = (job.title or "").replace("|", "-")
                company_clean = (job.company or "").replace("|", "-")
                loc_clean = (job.location or "").replace("|", "-")
                report_lines.append(
                    f"| {idx+1} | {title_clean} | {company_clean} | {loc_clean} | {job.match_score}% | {apply_text} |"
                )
                
            report_content = "\n".join(report_lines)
            with open("matched_jobs.md", "w", encoding="utf-8") as f:
                f.write(report_content)
            info("Saved matched_jobs.md report in workspace root.")
        except Exception as e:
            warning(f"Failed to save matched_jobs.md: {e}")

        return SearchResult(
            status="success",
            message=message,
            role=resume.preferred_role,
            location=location,
            total_jobs_found=len(jobs),
            total_jobs_returned=len(good_matches),
            search_time=elapsed_time,
            providers_used=providers,
            failed_providers=failed_providers,
            jobs=good_matches,
            grouped_jobs=grouped_jobs,
            learning_path=learning_path
        )

    except Exception as e:
        exception(f"Job search failed: {e}")
        raise JobSearchError(str(e))

# ==========================================================
# Filter Location
# ==========================================================

def filter_location(
    jobs: List[JobData],
    location: str,
) -> List[JobData]:
    """
    Filter jobs by location. If local matches are found, exclude remote.
    """
    if not location:
        return jobs

    from services.location_parser import is_remote

    loc_lower = location.lower()

    # Find explicitly local jobs (excluding remote)
    local_jobs = [
        job
        for job in jobs
        if job.location and loc_lower in job.location.lower() and not is_remote(job.location)
    ]

    # If we found local matches, return them (don't show global remote)
    if local_jobs:
        return local_jobs

    # Otherwise, fall back to remote jobs
    return [
        job
        for job in jobs
        if is_remote(job.location)
    ]

# ==========================================================
# Filter Match Score
# ==========================================================

def filter_match_score(
    jobs: List[JobData],
    minimum_score: float = MIN_MATCH_SCORE,
) -> List[JobData]:

    return [
        job
        for job in jobs
        if job.match_score >= minimum_score
    ]

# ==========================================================
# Sort Jobs
# ==========================================================

def sort_jobs(
    jobs: List[JobData],
) -> List[JobData]:
    """
    Sort jobs by match score.
    """

    return sorted(
        jobs,
        key=lambda job: job.match_score,
        reverse=True,
    )

# ==========================================================
# Search Statistics
# ==========================================================

def search_statistics(
    jobs: List[JobData],
) -> dict:
    """
    Return search statistics.
    """

    if not jobs:
        return {
            "total_jobs": 0,
            "matched_jobs": 0,
            "highest_score": 0,
            "average_score": 0,
        }

    scores = [
        job.match_score
        for job in jobs
    ]

    matched = [
        job
        for job in jobs
        if job.match_score >= MIN_MATCH_SCORE
    ]

    return {
        "total_jobs": len(jobs),
        "matched_jobs": len(matched),
        "highest_score": max(scores),
        "average_score": round(
            sum(scores) / len(scores),
            2,
        ),
    }

# ==========================================================
# Search Summary
# ==========================================================

def search_summary(
    result: SearchResult,
) -> str:

    if result.status != "success":
        return result.message

    return (
        f"Found {result.total_jobs_found} jobs. "
        f"Returned {result.total_jobs_returned} matching jobs."
    )

# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":
    resume = ResumeData(
        name="Beere Vishnu Sai",
        preferred_role="Data Analyst",
        preferred_location="Hyderabad",
        experience_years=2,
        skills=[
            "Python",
            "SQL",
            "Power BI",
            "Excel",
            "Tableau",
        ],
    )

    result = search_jobs(
        resume,
    )

    print("\n" + "=" * 60)
    print(" AI JobAgent - Job Search ")
    print("=" * 60)
    print(
        search_summary(
            result
        )
    )
    print()

    for job in result.jobs[:10]:
        print(
            f"{job.company}"
            f" | "
            f"{job.title}"
            f" | "
            f"{job.match_score}%"
        )

    print()
    print(
        search_statistics(
            result.jobs
        )
    )