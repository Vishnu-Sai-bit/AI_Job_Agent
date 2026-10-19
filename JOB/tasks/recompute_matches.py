from datetime import datetime, timezone
from typing import Dict, Any, Optional
from extensions import db
from models.user import User
from models.resume import Resume
from models.job import Job
from models.job_match import JobMatch
from services.job_matcher import JobMatcher
from utils.logging_config import logger

def utc_now():
    return datetime.now(timezone.utc)

def recompute_user_matches(user: User, resume: Optional[Resume] = None) -> Dict[str, Any]:
    """
    Recalculates explainable match scores for all active jobs against the user's active resume.
    """
    target_resume = resume or user.get_active_resume()
    if not target_resume:
        return {"status": "no_resume", "matches_calculated": 0}

    profile = user.candidate_profile
    matcher = JobMatcher()
    active_jobs = Job.query.filter_by(status="active").all()
    count = 0

    for job in active_jobs:
        try:
            res = matcher.compute_match(target_resume, profile, job)
            existing_match = JobMatch.query.filter_by(
                user_id=user.id,
                resume_id=target_resume.id,
                job_id=job.id
            ).first()

            if existing_match:
                existing_match.match_score = res["match_score"]
                existing_match.score_breakdown = res["score_breakdown"]
                existing_match.skill_match_details = res["skill_match_details"]
                existing_match.match_explanation = res["match_explanation"]
                existing_match.eligibility_flags = res["eligibility_flags"]
            else:
                new_match = JobMatch(
                    user_id=user.id,
                    resume_id=target_resume.id,
                    job_id=job.id,
                    match_score=res["match_score"],
                    score_breakdown=res["score_breakdown"],
                    skill_match_details=res["skill_match_details"],
                    match_explanation=res["match_explanation"],
                    eligibility_flags=res["eligibility_flags"],
                    created_at=utc_now()
                )
                db.session.add(new_match)
            count += 1
        except Exception as e:
            logger.error(f"Error computing match for user {user.id} and job {job.id}: {e}")

    db.session.commit()
    return {"status": "success", "matches_calculated": count}
