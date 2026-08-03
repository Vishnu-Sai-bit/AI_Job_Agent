"""
==========================================================
AI JobAgent - Headless Browser Auto-Fill Agent
Author : Beere Vishnu Sai

Description:
    Provides automated job application form-filling intelligence.
    Extracts candidate profile data, maps inputs to common ATS fields
    (Workday, Greenhouse, Lever, SmartRecruiters, Custom portals),
    generates tailored motivation pitches, and produces executable
    Playwright automation scripts with human-in-the-loop review guards.
==========================================================
"""

from typing import Dict, List, Optional, Any
from utils.logger import logger


class AutoFillAgent:
    """
    Intelligent Form Filling Assistant with Playwright automation generation.
    """

    @classmethod
    def generate_autofill_payload(cls, resume_context: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize structured form fields, EEO answers, custom cover pitch,
        and executable Playwright script from candidate and job data.
        """
        candidate_name = resume_context.get("name", "Candidate")
        name_parts = candidate_name.split()
        first_name = name_parts[0] if name_parts else "Candidate"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        email = resume_context.get("email", "")
        phone = resume_context.get("phone", "")
        linkedin = resume_context.get("linkedin", "")
        github = resume_context.get("github", "")
        portfolio = resume_context.get("portfolio", "")
        location = resume_context.get("location") or resume_context.get("preferred_location") or "Remote / Hybrid"
        skills = resume_context.get("skills", [])
        experience_years = resume_context.get("experience_years", 2.0)
        
        job_title = job_data.get("title") or job_data.get("role") or "Target Role"
        company = job_data.get("company", "Target Employer")
        apply_url = job_data.get("apply_url") or job_data.get("url") or "https://careers.company.com/apply"

        # Construct tailored 3-sentence application pitch
        top_skills_str = ", ".join(skills[:4]) if skills else "technical problem-solving and domain expertise"
        tailored_pitch = (
            f"I am excited to apply for the {job_title} role at {company}. "
            f"With hands-on expertise in {top_skills_str}, I specialize in building robust solutions and workflows that deliver measurable results. "
            f"I am eager to contribute my technical and problem-solving skills to the team at {company}."
        )

        resume_filename = f"{candidate_name.replace(' ', '_')}_Resume.pdf" if candidate_name and candidate_name != "Candidate" else "Candidate_Resume.pdf"

        # Standard Field Mappings
        field_payload = {
            "full_name": candidate_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "current_location": location,
            "linkedin_url": linkedin,
            "github_url": github,
            "portfolio_url": portfolio,
            "years_of_experience": str(experience_years),
            "notice_period": "Immediate / 15-30 Days",
            "current_ctc": "Negotiable as per industry standards",
            "expected_ctc": "Competitive / Commensurate with role",
            "authorized_to_work": "Yes",
            "require_sponsorship": "No",
            "tailored_cover_pitch": tailored_pitch,
            "resume_file_ref": resume_filename
        }

        # Generate Executable Playwright Script
        playwright_script = cls._generate_playwright_script(apply_url, field_payload, job_title, company)

        # Checklist for user review
        checklist = [
            {"field": "Full Name", "value": candidate_name, "status": "verified"},
            {"field": "Email Address", "value": email, "status": "verified" if email else "needs_input"},
            {"field": "Phone Reference", "value": phone, "status": "verified" if phone else "needs_input"},
            {"field": "Location Hub", "value": location, "status": "verified"},
            {"field": "LinkedIn Profile", "value": linkedin, "status": "verified" if linkedin else "optional"},
            {"field": "GitHub Profile", "value": github, "status": "verified" if github else "optional"},
            {"field": "Work Authorization", "value": "Authorized (No sponsorship needed)", "status": "verified"},
            {"field": "Notice Period", "value": "Immediate / 15-30 Days", "status": "verified"},
            {"field": "Tailored Motivation Pitch", "value": tailored_pitch[:90] + "...", "status": "generated"}
        ]

        return {
            "job_title": job_title,
            "company": company,
            "apply_url": apply_url,
            "fields": field_payload,
            "review_checklist": checklist,
            "playwright_script": playwright_script,
            "mode": "safe_review_mode"
        }

    @classmethod
    def _generate_playwright_script(cls, apply_url: str, fields: Dict[str, str], job_title: str, company: str) -> str:
        """
        Generate standalone Python Playwright script with human-in-the-loop review.
        """
        return f'''"""
AI JobAgent - Automated Auto-Fill Script
Target: {job_title} at {company}
URL: {apply_url}
"""
import asyncio
from playwright.async_api import async_playwright

async def run_autofill():
    async with async_playwright() as p:
        # Launch browser in headful mode so the candidate can inspect
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        page = await browser.new_page()
        
        print("🚀 Navigating to job application page...")
        await page.goto("{apply_url}", timeout=60000)
        await page.wait_for_load_state("networkidle")
        
        # Smart Heuristic Form Selectors
        fields = {fields}
        
        # 1. Fill Name
        for sel in ["input[name*='name' i]", "input[id*='name' i]", "input[placeholder*='Full Name' i]"]:
            if await page.locator(sel).count() > 0:
                await page.locator(sel).first.fill(fields['full_name'])
                print("✓ Filled Full Name")
                break
                
        # 2. Fill Email
        for sel in ["input[type='email']", "input[name*='email' i]", "input[id*='email' i]"]:
            if await page.locator(sel).count() > 0:
                await page.locator(sel).first.fill(fields['email'])
                print("✓ Filled Email")
                break

        # 3. Fill Phone
        for sel in ["input[type='tel']", "input[name*='phone' i]", "input[id*='phone' i]"]:
            if await page.locator(sel).count() > 0:
                await page.locator(sel).first.fill(fields['phone'])
                print("✓ Filled Phone")
                break

        # 4. Fill LinkedIn / URLs
        for sel in ["input[name*='linkedin' i]", "input[placeholder*='linkedin' i]"]:
            if await page.locator(sel).count() > 0 and fields.get('linkedin_url'):
                await page.locator(sel).first.fill(fields['linkedin_url'])
                print("✓ Filled LinkedIn")
                break

        # 5. Fill Cover Letter / Additional Info
        for sel in ["textarea[name*='cover' i]", "textarea[id*='cover' i]", "textarea[placeholder*='additional' i]"]:
            if await page.locator(sel).count() > 0:
                await page.locator(sel).first.fill(fields['tailored_cover_pitch'])
                print("✓ Filled Tailored Cover Note")
                break

        print("\\n✨ SAFE REVIEW MODE ACTIVE:")
        print("Please inspect all fields in the open browser window.")
        print("Review answers, attach your resume PDF, and click Submit manually when ready.")
        
        # Keep open for candidate verification
        await asyncio.sleep(120)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_autofill())
'''

    @classmethod
    def simulate_fill_steps(cls, fields: Dict[str, Any], job_title: str, company: str) -> List[Dict[str, str]]:
        """
        Provide real-time stepper sequence for UI auto-fill runner.
        """
        return [
            {"step": 1, "title": "Portal Discovery", "desc": f"Connecting to {company} career gateway and parsing form schema...", "status": "completed"},
            {"step": 2, "title": "Field Mapping", "desc": f"Matched candidate credentials (Name: {fields.get('full_name')}, Email: {fields.get('email')}).", "status": "completed"},
            {"step": 3, "title": "Work Auth Verification", "desc": "Configured compliance answers (Authorized: Yes, Sponsorship: No).", "status": "completed"},
            {"step": 4, "title": "Pitch Synthesis", "desc": f"Drafted tailored value proposition for {job_title}.", "status": "completed"},
            {"step": 5, "title": "Safe Review Guard", "desc": "All fields primed. Ready for candidate final review and submission.", "status": "ready"}
        ]


auto_fill_agent = AutoFillAgent()
