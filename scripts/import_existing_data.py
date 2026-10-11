"""
==========================================================
Script - Import Existing Data
==========================================================
"""

import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db
from app.models.job import Job

app = create_app()

with app.app_context():
    export_file = ROOT_DIR / "data" / "jobs_export.json"
    if export_file.exists():
        with open(export_file, "r", encoding="utf-8") as f:
            jobs_data = json.load(f)
        count = 0
        for j in jobs_data:
            job_id = str(j.get("id"))
            if not db.session.get(Job, job_id):
                job_record = Job(
                    id=job_id,
                    title=j.get("title", ""),
                    company=j.get("company", ""),
                    location=j.get("location", ""),
                    salary=j.get("salary", "Competitive"),
                    experience=j.get("experience", "1-3 yrs"),
                    source=j.get("source", "Aggregator"),
                    url=j.get("url", "#"),
                    skills=j.get("skills") or [],
                    description=j.get("description", "")
                )
                db.session.add(job_record)
                count += 1
        db.session.commit()
        print(f"Imported {count} verified job listings into database.")
    else:
        print("data/jobs_export.json not found.")
