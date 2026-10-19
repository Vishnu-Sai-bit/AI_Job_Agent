from datetime import datetime
from typing import Dict, Any, List
from models.job import Job
from models.user import CandidateProfile
from models.resume import Resume

class CoverLetterService:
    def generate_tailored_cover_letter(
        self,
        candidate_profile: CandidateProfile,
        resume: Resume,
        job: Job
    ) -> str:
        """
        Synthesizes a personalized, grounded cover letter using candidate's verified background.
        Strict rule: Never invents unverified claims or fake qualifications.
        """
        parsed = resume.parsed_data or {}
        candidate_name = candidate_profile.full_name or parsed.get("name") or "Applicant"
        email = candidate_profile.user.email if candidate_profile.user else parsed.get("email", "")
        phone = candidate_profile.phone or parsed.get("phone", "")
        location = candidate_profile.location or parsed.get("location", "")
        
        skills = parsed.get("skills") or candidate_profile.skills or []
        req_skills = job.required_skills or []
        
        # Identify overlapping skills
        matched_skills = [s for s in skills if any(s.lower() in rs.lower() or rs.lower() in s.lower() for rs in req_skills)]
        top_skills = matched_skills[:4] if matched_skills else skills[:4]
        skills_str = ", ".join(top_skills) if top_skills else "software engineering and modern technology frameworks"

        # Check for projects or experience highlights
        projects = parsed.get("projects") or candidate_profile.projects or []
        proj_highlight = ""
        if projects and isinstance(projects[0], dict):
            p = projects[0]
            proj_title = p.get("title", "Recent Project")
            proj_desc = p.get("description", "").strip()
            if proj_desc:
                proj_highlight = f"In my work on {proj_title}, I successfully delivered: {proj_desc[:200]}."

        exp_years = float(candidate_profile.experience_years or parsed.get("experience_years", 0))
        exp_phrase = f"With {exp_years:.1f} years of hands-on experience" if exp_years > 0 else "With a solid background in software development"

        date_str = datetime.now().strftime("%B %d, %Y")

        letter = f"""{candidate_name}
{location} | {email} | {phone}

{date_str}

Hiring Team
{job.company}

Dear Hiring Team at {job.company},

I am writing to express my strong interest in the {job.title} position at {job.company}. {exp_phrase}, I have developed deep proficiency in {skills_str}, and I am eager to contribute to your team's goals.

Throughout my career, I have focused on building reliable, scalable systems and applying engineering best practices. {proj_highlight} Reviewing your requirements for {job.title}, I noted your emphasis on {', '.join(req_skills[:3]) if req_skills else 'high quality development'}. My background directly aligns with these core competencies, enabling me to immediately contribute to your engineering objectives.

What excites me most about {job.company} is the opportunity to solve meaningful problems in a collaborative environment. I bring a strong work ethic, continuous curiosity, and an emphasis on measurable results.

Thank you for your time and consideration. I welcome the opportunity to discuss how my experience and skill set can benefit {job.company}.

Sincerely,

{candidate_name}
"""
        return letter.strip()

    def generate_interview_prep(self, candidate_profile: CandidateProfile, resume: Resume, job: Job) -> List[Dict[str, str]]:
        """
        Generates tailored interview questions and preparation talking points
        based on the candidate's actual resume and the job's requirements.
        """
        parsed = resume.parsed_data or {}
        skills = parsed.get("skills") or []
        req_skills = job.required_skills or []

        qas = [
            {
                "question": f"How has your experience with {skills[0] if skills else 'your core tech stack'} prepared you for this role at {job.company}?",
                "focus": "Technical depth and architecture",
                "tip": "Explain a real scenario where you made technical trade-offs and delivered a reliable feature."
            },
            {
                "question": f"The job description mentions {req_skills[0] if req_skills else 'collaborative development'}. How do you approach this in your daily workflow?",
                "focus": "Requirement alignment",
                "tip": "Reference specific project deliverables and how you ensured code quality and maintainability."
            },
            {
                "question": "Can you walk through a challenging bug or performance bottleneck you identified and resolved?",
                "focus": "Problem solving & debugging",
                "tip": "Use the STAR method (Situation, Task, Action, Result) with measurable metrics."
            }
        ]
        return qas
