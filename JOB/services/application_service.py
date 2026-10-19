from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from extensions import db
from models.application import Application, ApplicationDocument
from models.job_match import SavedJob
from models.job import Job

VALID_STATUSES = ["saved", "prepared", "applied", "interviewing", "offer", "rejected", "withdrawn"]

def utc_now():
    return datetime.now(timezone.utc)

class ApplicationService:
    def get_or_create_application(self, user_id: int, job_id: int, status: str = "prepared") -> Application:
        app = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
        if not app:
            app = Application(
                user_id=user_id,
                job_id=job_id,
                status=status if status in VALID_STATUSES else "prepared",
                created_at=utc_now()
            )
            db.session.add(app)
            db.session.commit()
        return app

    def update_application_status(
        self,
        user_id: int,
        application_id: int,
        status: str,
        notes: Optional[str] = None,
        next_action_at: Optional[datetime] = None,
        next_action_desc: Optional[str] = None,
        is_verified: bool = False
    ) -> Application:
        app = Application.query.filter_by(id=application_id, user_id=user_id).first_or_404()
        if status in VALID_STATUSES:
            app.status = status
            if status == "applied" and not app.submitted_at:
                app.submitted_at = utc_now()

        if notes is not None:
            app.notes = notes
        if next_action_at is not None:
            app.next_action_at = next_action_at
        if next_action_desc is not None:
            app.next_action_description = next_action_desc

        app.is_integration_verified = is_verified
        app.updated_at = utc_now()
        db.session.commit()
        return app

    def toggle_saved_job(self, user_id: int, job_id: int, notes: str = "") -> bool:
        existing = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return False
        else:
            saved = SavedJob(user_id=user_id, job_id=job_id, notes=notes)
            db.session.add(saved)
            db.session.commit()
            return True

    def get_applications_grouped_by_status(self, user_id: int) -> Dict[str, List[Application]]:
        apps = Application.query.filter_by(user_id=user_id).order_by(Application.updated_at.desc()).all()
        grouped = {s: [] for s in VALID_STATUSES}
        for a in apps:
            if a.status in grouped:
                grouped[a.status].append(a)
        return grouped
