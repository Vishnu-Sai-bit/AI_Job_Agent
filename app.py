"""
==========================================================
AI Job Agent - Flask Application (app.py)
Direct verified application redirection with internal ID lookup.
==========================================================
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template, redirect, abort, url_for, jsonify
from models import db, Job
from job_service import select_apply_url, validate_official_url, check_job_link, save_job

app = Flask(__name__)

# Ensure instance directory exists
instance_path = Path(__file__).resolve().parent / "instance"
instance_path.mkdir(exist_ok=True)

# SQLite database or environment DATABASE_URL
db_uri = os.getenv("DATABASE_URL", f"sqlite:///{instance_path / 'ai_jobs.db'}")
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def seed_initial_jobs():
    """Seed real verified vacancies from data/jobs_export.json if empty."""
    export_file = Path(__file__).resolve().parent / "data" / "jobs_export.json"
    if export_file.exists():
        try:
            with open(export_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data[:30]:
                try:
                    s_id = str(item.get("job_id") or item.get("external_job_id") or item.get("id") or "").strip()
                    orig_url = str(item.get("official_job_url") or item.get("url") or "").strip()
                    app_url = str(item.get("apply_url") or orig_url).strip()
                    
                    if s_id and orig_url:
                        save_job({
                            "source_platform": item.get("ats_provider") or item.get("source") or "Company Careers",
                            "source_job_id": s_id,
                            "company_name": item.get("company_name") or item.get("company") or "Employer",
                            "title": item.get("job_title") or item.get("title") or "Software Engineer",
                            "location": item.get("location") or "Remote / Office",
                            "original_url": orig_url,
                            "apply_url": app_url,
                            "is_active": True,
                            "link_status": "verified" if item.get("url_verified") else "unverified"
                        })
                except Exception:
                    pass
        except Exception:
            pass


with app.app_context():
    db.create_all()
    if Job.query.count() == 0:
        seed_initial_jobs()


@app.route("/")
@app.route("/jobs")
def home():
    """List all active vacancies ordered by first seen date descending."""
    jobs = (
        Job.query
        .filter_by(is_active=True)
        .order_by(Job.first_seen_at.desc())
        .all()
    )
    return render_template("jobs.html", jobs=jobs)


@app.route("/apply/<int:job_id>")
def apply_to_job(job_id: int):
    """
    Safely redirect candidate to the employer's official job/application page.
    Uses the internal database primary key (job_id) to look up the stored record.
    Prevents open-redirect vulnerabilities.
    """
    job = db.session.get(Job, job_id)
    if job is None or not job.is_active:
        abort(404)

    target_url = select_apply_url(job)
    if not target_url or not validate_official_url(target_url):
        abort(404)

    return redirect(target_url, code=302)


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "AI Job Agent",
        "active_jobs_count": Job.query.filter_by(is_active=True).count()
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
