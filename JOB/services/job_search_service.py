from typing import Optional, List, Dict, Any
from sqlalchemy import or_, and_, desc
from extensions import db
from models.job import Job
from models.job_match import JobMatch
from models.user import User

class JobSearchService:
    def search_jobs(
        self,
        user: Optional[User] = None,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        work_mode: Optional[str] = None,
        platform: Optional[str] = None,
        experience_level: Optional[str] = None,
        min_match_score: Optional[float] = None,
        status: str = "active",
        page: int = 1,
        per_page: int = 12,
        sort_by: str = "match"
    ) -> Dict[str, Any]:
        """
        Queries and filters jobs with match scores for the given candidate.
        """
        active_resume = user.get_active_resume() if user else None

        query = Job.query
        if status:
            query = query.filter(Job.status == status)

        # Multi-term keyword filtering
        if keyword:
            terms = [t.strip().lower() for t in keyword.split() if len(t.strip()) > 1]
            # Ignore generic words if specific tech words are present
            tech_terms = [t for t in terms if t not in ("developer", "engineer", "software", "jobs", "job", "position")]
            effective_terms = tech_terms if tech_terms else terms
            
            for term in effective_terms:
                kw = f"%{term}%"
                query = query.filter(
                    or_(
                        Job.title.ilike(kw),
                        Job.company.ilike(kw),
                        Job.department.ilike(kw),
                        Job.description.ilike(kw)
                    )
                )

        if location:
            loc = f"%{location.strip().lower()}%"
            query = query.filter(
                or_(
                    Job.location.ilike(loc),
                    Job.country.ilike(loc),
                    Job.city.ilike(loc)
                )
            )

        if work_mode and work_mode.lower() != "all":
            query = query.filter(Job.work_mode == work_mode.lower())

        if platform and platform.lower() != "all":
            query = query.filter(Job.source_platform == platform.lower())

        if experience_level and experience_level.lower() != "all":
            query = query.filter(Job.experience_level == experience_level.lower())

        if active_resume:
            query = query.outerjoin(
                JobMatch,
                and_(
                    JobMatch.job_id == Job.id,
                    JobMatch.user_id == user.id,
                    JobMatch.resume_id == active_resume.id
                )
            )
            if min_match_score is not None:
                query = query.filter(JobMatch.match_score >= float(min_match_score))

            if sort_by == "match":
                query = query.order_by(desc(JobMatch.match_score), desc(Job.published_at), desc(Job.id))
            else:
                query = query.order_by(desc(Job.published_at), desc(Job.id))
        else:
            query = query.order_by(desc(Job.published_at), desc(Job.id))

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        results = []
        user_saved_ids = set()
        user_applied_ids = set()

        if user:
            user_saved_ids = {s.job_id for s in user.saved_jobs.all()}
            user_applied_ids = {a.job_id for a in user.applications.all()}

        for job in paginated.items:
            match_obj = None
            if active_resume:
                match_obj = JobMatch.query.filter_by(
                    user_id=user.id,
                    resume_id=active_resume.id,
                    job_id=job.id
                ).first()

            results.append({
                "job": job,
                "match": match_obj,
                "is_saved": job.id in user_saved_ids,
                "is_applied": job.id in user_applied_ids
            })

        return {
            "jobs": results,
            "items": results,
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev
        }
