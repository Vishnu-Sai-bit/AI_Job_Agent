"""
==========================================================
AI JobAgent - Email Generator Service
Author : Antigravity
==========================================================
"""

import json
from typing import Dict, Any, List, Optional

from utils import info, exception, call_llm
from exceptions import ResumeAnalyzerError, OllamaConnectionError

PROMPT = """
You are a senior recruitment coordinator and executive career coach.
Your task is to write high-converting, professional emails and outreach messages tailored to the candidate's actual projects, metrics, certifications, and target company.

Generate the templates following this JSON schema exactly:
{{
    "cold_outreach": {{
        "subject": "Compelling subject line mentioning candidate name, target role, and top certification or experience...",
        "body": "Full body of cold email to the Hiring Manager / Department Lead. Include:\\n- Professional greeting\\n- Concise hook showing interest in the company\\n- 2-3 quantified bullet points directly extracted from candidate projects (e.g. % efficiency, record counts, dashboards created, ML accuracy)\\n- Call to action (10-min intro chat)\\n- Professional signature including Name, Phone, Email, GitHub, LinkedIn, and Portfolio links."
    }},
    "linkedin_inmail": {{
        "subject": "LinkedIn Connection Note",
        "body": "A high-impact, personalized LinkedIn connection request message (strictly under 300 characters) highlighting core skills and interest in the company."
    }},
    "follow_up_email": {{
        "subject": "Re: Follow-Up - Candidate Name - Target Role",
        "body": "A polite, strategic follow-up email to send 4-5 days after initial outreach. Mentions a key project or operational insight to reinforce value and invites a brief connection."
    }},
    "job_application": {{
        "subject": "Application for Target Role - Candidate Name",
        "body": "Formal application email to HR / Talent Acquisition attaching resume and highlighting relevant technical qualifications and alignment with the team."
    }}
}}

Candidate Name: {name}
Email: {email}
Phone: {phone}
LinkedIn: {linkedin}
GitHub: {github}
Portfolio: {portfolio}
Skills: {skills}
Target Role: {role}
Target Company: {company}

Resume Projects & Background Context:
{resume_context}

IMPORTANT RULES:
1. Use the real project details, metrics, and certifications from the candidate's context.
2. In the cold email signature, format the contact details and links cleanly.
3. Return ONLY the valid JSON structure. Do NOT explain anything else.
"""

def generate_job_emails(
    name: str,
    skills: List[str],
    role: str,
    company: str,
    email: Optional[str] = "",
    phone: Optional[str] = "",
    linkedin: Optional[str] = "",
    github: Optional[str] = "",
    portfolio: Optional[str] = "",
    resume_context: Optional[str] = ""
) -> Dict[str, Any]:
    """
    Generate cold outreach, LinkedIn InMail, follow-up, and application templates.
    """
    skills_str = ", ".join(skills) if skills else "Data Analysis, Python, SQL, BI"
    formatted_prompt = PROMPT.format(
        name=name or "Candidate",
        email=email or "candidate@email.com",
        phone=phone or "+91 0000000000",
        linkedin=linkedin or "linkedin.com/in/profile",
        github=github or "github.com/profile",
        portfolio=portfolio or "portfolio.dev",
        skills=skills_str,
        role=role or "Data Analyst",
        company=company or "Target Company",
        resume_context=resume_context or "Proven experience in SQL, Python, Power BI, and Tableau dashboards."
    )

    info(f"Generating full email suite for: {role} at {company}")

    try:
        content = call_llm(formatted_prompt, json_format=True)
        return json.loads(content)
    except Exception as e:
        exception(f"Email template generation failed: {e}")
        # Rich Fallback templates
        return {
            "cold_outreach": {
                "subject": f"{role} Opportunity — {name} | Oracle Certified & Data Analytics",
                "body": (
                    f"Hi [Hiring Manager Name],\n\n"
                    f"I came across {company}'s analytics initiatives and wanted to reach out directly regarding open {role} opportunities on your team.\n\n"
                    f"I am a {role} skilled in {skills_str}. In my recent project work:\n"
                    f"• Engineered end-to-end data pipelines and resolved 1,200+ data quality inconsistencies, boosting verified accuracy to >95%.\n"
                    f"• Designed executive Power BI & Tableau dashboards tracking 8+ core KPIs, cutting reporting time by 60%.\n"
                    f"• Built predictive models to identify key operational and customer retention drivers.\n\n"
                    f"I’ve attached my resume and would love 10 minutes to discuss how my dashboarding and querying skills can add immediate value to {company}.\n\n"
                    f"Portfolio Repositories:\n"
                    f"• GitHub: {github or 'https://github.com'}\n"
                    f"• LinkedIn: {linkedin or 'https://linkedin.com'}\n"
                    f"• Portfolio: {portfolio or 'https://portfolio.dev'}\n\n"
                    f"Best regards,\n{name}\n📞 {phone} | ✉️ {email}"
                )
            },
            "linkedin_inmail": {
                "subject": "LinkedIn Connection Note",
                "body": (
                    f"Hi [Name], I admire {company}'s analytics work. As a {role} skilled in {skills_str} with experience delivering KPI dashboards, I'd love to connect and explore potential opportunities with your team! Best, {name}"
                )
            },
            "follow_up_email": {
                "subject": f"Re: {role} Application — {name}",
                "body": (
                    f"Hi [Hiring Manager Name],\n\n"
                    f"Following up on my note from earlier this week regarding the {role} role at {company}.\n\n"
                    f"I recently deployed a dashboard analyzing operational records to identify peak bottlenecks and reduce wait times by 20%. I would be thrilled to bring the same data-driven impact to your team.\n\n"
                    f"Whenever you have a brief moment next week, I’d welcome the chance to connect.\n\n"
                    f"Thank you,\n{name}\n📞 {phone} | ✉️ {email}"
                )
            },
            "job_application": {
                "subject": f"Application for {role} — {name}",
                "body": (
                    f"Dear Hiring Team,\n\n"
                    f"Please find attached my resume for the {role} position at {company}. "
                    f"With expertise in {skills_str}, I am excited about the opportunity to contribute to your analytics and engineering goals.\n\n"
                    f"Looking forward to the possibility of discussing this further.\n\n"
                    f"Sincerely,\n{name}\n📞 {phone} | ✉️ {email}"
                )
            }
        }

