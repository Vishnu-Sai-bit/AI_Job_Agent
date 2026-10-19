import re
from typing import Dict, Any, List, Optional
from extensions import db
from models.user import User
from models.job import Job
from models.job_match import JobMatch
from models.application import Application
from services.job_search_service import JobSearchService
from services.cover_letter_service import CoverLetterService
from services.ats_scorer import ATSScorer

class CareerAssistant:
    def __init__(self):
        self.search_service = JobSearchService()
        self.cover_letter_service = CoverLetterService()
        self.ats_scorer = ATSScorer()

    def process_message(self, user: User, message: str, context_job_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Processes conversational commands and returns responses grounded in real candidate and job data.
        """
        msg = message.strip()
        lowered = msg.lower()
        active_resume = user.get_active_resume()

        # 1. Saved Jobs query
        if "saved job" in lowered or "my saved" in lowered or "bookmarked" in lowered:
            return self._handle_saved_jobs(user)

        # 2. Application status query
        if "application" in lowered and ("status" in lowered or "history" in lowered or "track" in lowered or "stage" in lowered):
            return self._handle_application_status(user)

        # 3. Resume improvement / ATS feedback
        if ("improve" in lowered and "resume" in lowered) or "ats" in lowered or ("quality" in lowered and "resume" in lowered):
            return self._handle_resume_advice(user, active_resume)

        # 4. Cover Letter request
        if "cover letter" in lowered:
            return self._handle_cover_letter(user, active_resume, context_job_id, msg)

        # 5. Missing skills / Gap analysis
        if "missing" in lowered or "skill gap" in lowered or "gap" in lowered:
            return self._handle_missing_skills(user, active_resume, context_job_id)

        # 6. Interview preparation
        if "interview" in lowered or "questions" in lowered:
            return self._handle_interview_prep(user, active_resume, context_job_id)

        # 7. Job Search commands
        return self._handle_conversational_search(user, msg)

    def _handle_saved_jobs(self, user: User) -> Dict[str, Any]:
        saved_items = user.saved_jobs.all()
        if not saved_items:
            return {
                "reply": "You don't have any saved jobs yet. You can bookmark jobs anytime by clicking the bookmark icon on any job card.",
                "type": "text",
                "cards": []
            }
        
        cards = []
        for s in saved_items[:6]:
            job = s.job
            cards.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "source": job.source_platform,
                "original_url": job.original_url,
                "apply_url": f"/apply/{job.id}"
            })
        return {
            "reply": f"You currently have {len(saved_items)} saved job{'s' if len(saved_items) > 1 else ''}:",
            "type": "job_list",
            "cards": cards
        }

    def _handle_application_status(self, user: User) -> Dict[str, Any]:
        apps = user.applications.all()
        if not apps:
            return {
                "reply": "You haven't tracked any applications yet. When you prepare or apply for a position, record it in your Application Tracker.",
                "type": "text",
                "cards": []
            }

        counts = {}
        for a in apps:
            counts[a.status] = counts.get(a.status, 0) + 1
        
        summary_lines = [f"- **{status.title()}**: {cnt}" for status, cnt in counts.items()]
        reply = f"Here is your current application pipeline ({len(apps)} total):\n" + "\n".join(summary_lines)
        return {
            "reply": reply,
            "type": "text",
            "cards": []
        }

    def _handle_resume_advice(self, user: User, resume) -> Dict[str, Any]:
        if not resume:
            return {
                "reply": "Please upload a resume first so I can analyze its completeness, readability, and ATS metrics.",
                "type": "text",
                "cards": []
            }
        
        feedback = resume.ats_feedback or {}
        action_tips = feedback.get("actionable_feedback", [])
        score = resume.ats_quality_score or 75.0

        reply = f"**Resume Quality Assessment ({score:.0f}/100)**\n\n"
        if action_tips:
            reply += "Key improvement recommendations:\n"
            for tip in action_tips[:4]:
                reply += f"- {tip}\n"
        else:
            reply += "Your resume has solid section completeness and readability. Ensure each bullet point highlights quantifiable outcomes."

        return {
            "reply": reply,
            "type": "text",
            "cards": []
        }

    def _handle_cover_letter(self, user: User, resume, context_job_id: Optional[int], msg: str) -> Dict[str, Any]:
        if not resume:
            return {
                "reply": "Please upload your resume first so I can generate a grounded cover letter without inventing qualifications.",
                "type": "text",
                "cards": []
            }

        job = None
        if context_job_id:
            job = db.session.get(Job, context_job_id)
        
        if not job:
            top_match = user.job_matches.order_by(JobMatch.match_score.desc()).first()
            if top_match:
                job = top_match.job
            else:
                job = Job.query.filter_by(status="active").first()

        if not job:
            return {
                "reply": "No job found to generate a cover letter for. Please search or select a job first.",
                "type": "text",
                "cards": []
            }

        letter = self.cover_letter_service.generate_tailored_cover_letter(
            user.candidate_profile,
            resume,
            job
        )
        return {
            "reply": f"Here is a tailored cover letter grounded in your verified experience for **{job.title}** at **{job.company}**:\n\n```text\n{letter}\n```",
            "type": "cover_letter",
            "job_id": job.id,
            "job_title": job.title,
            "company": job.company
        }

    def _handle_missing_skills(self, user: User, resume, context_job_id: Optional[int]) -> Dict[str, Any]:
        if not resume:
            return {
                "reply": "Please upload your resume so I can calculate your skill gap against specific positions.",
                "type": "text",
                "cards": []
            }

        job = db.session.get(Job, context_job_id) if context_job_id else None
        if not job:
            top_match = user.job_matches.order_by(JobMatch.match_score.desc()).first()
            if top_match:
                job = top_match.job

        if not job:
            return {
                "reply": "Please select a specific job from the Jobs page to see its detailed skill gap analysis.",
                "type": "text",
                "cards": []
            }

        match = JobMatch.query.filter_by(user_id=user.id, resume_id=resume.id, job_id=job.id).first()
        if not match:
            from services.job_matcher import JobMatcher
            matcher = JobMatcher()
            res = matcher.compute_match(resume, user.candidate_profile, job)
            missing = res["skill_match_details"].get("missing_required", [])
            matched = res["skill_match_details"].get("matched_required", [])
        else:
            details = match.skill_match_details or {}
            missing = details.get("missing_required", [])
            matched = details.get("matched_required", [])

        reply = f"**Skill Analysis for {job.title} at {job.company}**:\n\n"
        if matched:
            reply += f"✅ **Matched Skills on your resume**: {', '.join(matched)}\n\n"
        if missing:
            reply += f"⚠️ **Missing Evidence on your resume**: {', '.join(missing)}\n\n"
            reply += "Tip: If you possess experience with these tools, update your resume to include specific projects demonstrating your use of them."
        else:
            reply += "🎉 You have verified evidence for all primary required skills in this posting!"

        return {
            "reply": reply,
            "type": "text",
            "cards": []
        }

    def _handle_interview_prep(self, user: User, resume, context_job_id: Optional[int]) -> Dict[str, Any]:
        job = db.session.get(Job, context_job_id) if context_job_id else Job.query.filter_by(status="active").first()
        if not job or not resume:
            return {
                "reply": "Select a job to view tailored interview preparation questions.",
                "type": "text",
                "cards": []
            }
        
        qas = self.cover_letter_service.generate_interview_prep(user.candidate_profile, resume, job)
        reply = f"**Interview Preparation for {job.title} at {job.company}**:\n\n"
        for i, q in enumerate(qas, 1):
            reply += f"**{i}. {q['question']}**\n- *Focus*: {q['focus']}\n- *Strategy*: {q['tip']}\n\n"

        return {
            "reply": reply,
            "type": "text",
            "cards": []
        }

    def _handle_conversational_search(self, user: User, msg: str) -> Dict[str, Any]:
        lowered = msg.lower()
        
        # Extract minimum match threshold (e.g. 80% or 80)
        min_score = None
        score_match = re.search(r"(\d{1,3})%\s*(?:or higher|match|\+)?", lowered)
        if score_match:
            min_score = float(score_match.group(1))

        # Extract work mode or location
        work_mode = None
        if "remote" in lowered:
            work_mode = "remote"
        elif "hybrid" in lowered:
            work_mode = "hybrid"
        elif "on-site" in lowered or "onsite" in lowered:
            work_mode = "on-site"

        location = None
        if "in india" in lowered:
            location = "India"
        elif "in us" in lowered or "in usa" in lowered:
            location = "United States"
        elif "in uk" in lowered:
            location = "United Kingdom"
        elif "in germany" in lowered:
            location = "Germany"

        exp_level = None
        if "fresher" in lowered or "entry" in lowered or "junior" in lowered or "intern" in lowered:
            exp_level = "entry"
        elif "senior" in lowered or "lead" in lowered:
            exp_level = "senior"

        # Keyword extraction
        keyword = msg
        keyword = re.sub(r"\d{1,3}%", "", keyword)
        for stop in ["find", "show", "search for", "jobs", "job", "matching my resume", "with an", "or higher match", "or higher", "match", "fresher", "remote", "in india", "worldwide", "please"]:
            keyword = re.sub(r"(?i)\b" + re.escape(stop) + r"\b", "", keyword)
        keyword = keyword.strip()

        # Run query
        search_results = self.search_service.search_jobs(
            user=user,
            keyword=keyword if len(keyword) > 2 else None,
            location=location,
            work_mode=work_mode,
            experience_level=exp_level,
            min_match_score=min_score,
            page=1,
            per_page=5
        )

        items = search_results["jobs"]
        if not items:
            return {
                "reply": f"I couldn't find any active jobs matching '{msg}'. Try broadening your search or adjusting your match score threshold.",
                "type": "text",
                "cards": []
            }

        cards = []
        for it in items:
            job = it["job"]
            match = it["match"]
            score_val = match.match_score if match else None
            cards.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "work_mode": job.work_mode,
                "source": job.source_platform,
                "match_score": score_val,
                "explanation": match.match_explanation if match else "Review job description for requirements.",
                "apply_url": f"/apply/{job.id}"
            })

        reply = f"Found **{search_results['total']}** matching opportunities. Here are the top recommendations:"
        return {
            "reply": reply,
            "type": "job_list",
            "cards": cards
        }
