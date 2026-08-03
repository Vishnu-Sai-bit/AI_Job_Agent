"""
==========================================================
AI JobAgent - MongoDB Seed & Data Sync Script
Populates the `ai_job_agent` database in MongoDB on localhost:27017
==========================================================
"""

import sys
import io
from pathlib import Path

# Configure utf-8 stdout
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.db.mongo_manager import db_manager
from services.auth.auth_service import auth_service
from utils.logger import logger


def seed_database():
    print("=" * 60)
    print("🚀 Initializing AI JobAgent MongoDB Database (`ai_job_agent`)...")
    print("=" * 60)

    status = db_manager.get_status()
    print(f"📦 Storage Mode: {status['storage_mode']}")
    print(f"🗄️ Database Name: {status['database_name']}")
    print(f"🔌 Connected: {status['connected']}")

    # 1. Seed Users Collection
    print("\n[1/4] Seeding Users Collection (`users`)...")
    try:
        user_doc = {
            "name": "Beere Vishnu Sai",
            "email": "vishnusai@example.com",
            "password_hash": auth_service.hash_password("Vishnu@2026"),
            "role": "candidate",
            "hub": "Hyderabad, India"
        }
        user = db_manager.create_user(user_doc)
        user_id = user["id"]
        print(f"✓ Created candidate user: {user['name']} ({user['email']}) -> ID: {user_id}")
    except ValueError as e:
        existing = db_manager.get_user_by_email("vishnusai@example.com")
        user_id = existing["id"] if existing else "usr_vishnusai_01"
        print(f"ℹ User already exists: {user_id}")

    # 2. Seed Candidate Profile Collection
    print("\n[2/4] Seeding Candidate Profile (`candidate_profiles`)...")
    candidate_profile = {
        "name": "Beere Vishnu Sai",
        "email": "vishnusai@example.com",
        "phone": "+91 9876543210",
        "location": "Hyderabad, India",
        "preferred_location": "Hyderabad, India",
        "preferred_role": "Data Analyst",
        "career_level": "Entry / Mid-Level",
        "experience_years": 2.0,
        "education": [
            {
                "degree": "B.Tech in Information Technology",
                "institution": "JNTU Hyderabad",
                "year": "2024"
            }
        ],
        "skills": [
            "Python", "SQL", "Power BI", "Tableau", "Excel", "Pandas", "NumPy",
            "Scikit-Learn", "DAX", "Data Modeling", "Machine Learning", "FastAPI"
        ],
        "certifications": [
            "🏆 Oracle Cloud Infrastructure 2025 Certified AI Foundations Associate",
            "📊 Microsoft Certified: Power BI Data Analyst Associate"
        ],
        "projects": [
            {
                "title": "EV Charging Station Analysis",
                "description": "Designed end-to-end EDA pipeline on 30,000+ records and built interactive Tableau dashboards tracking 8+ utilization KPIs.",
                "tools": ["Python", "Tableau", "Pandas", "SQL"]
            },
            {
                "title": "Customer Churn Prediction",
                "description": "Built classification model achieving 87% accuracy with feature importance analysis in Scikit-Learn and Power BI reporting.",
                "tools": ["Python", "Machine Learning", "Power BI", "SQL"]
            },
            {
                "title": "AI Job Copilot & Career Intelligence",
                "description": "Engineered agentic career acceleration platform with ATS diagnostics, multi-source deduplication, and mock interview evaluation.",
                "tools": ["FastAPI", "MongoDB", "Python", "Playwright"]
            }
        ],
        "ats_score": 88,
        "career_summary": "Analytical and detail-oriented Data Analyst with expertise in Python, SQL, Power BI, and Tableau. Experienced in transforming complex datasets into actionable executive insights and automated KPI dashboards.",
        "linkedin": "https://linkedin.com/in/vishnusai",
        "github": "https://github.com/Vishnu-Sai-bit"
    }

    saved_prof = db_manager.save_candidate_profile(user_id, candidate_profile)
    print(f"✓ Saved candidate profile for {candidate_profile['name']} (ATS Score: {candidate_profile['ats_score']}%)")

    # 3. Seed Application Pipeline CRM (`applications`)
    print("\n[3/4] Seeding Application Pipeline CRM (`applications`)...")
    sample_applications = [
        {
            "id": "app_deloitte_01",
            "user_id": user_id,
            "company": "Deloitte",
            "role": "Business Intelligence Analyst",
            "location": "Hyderabad, India",
            "salary": "₹8.5L - ₹11L PA",
            "apply_url": "https://jobs.deloitte.com/job/hyderabad-bi-analyst",
            "status": "offer",
            "date_applied": "2026-09-15",
            "followup_date": "2026-09-22",
            "interview_date": "2026-09-28",
            "notes": "Offer letter received. Excellent team culture and modern cloud stack."
        },
        {
            "id": "app_codetech_02",
            "user_id": user_id,
            "company": "CodeTech",
            "role": "Python Developer",
            "location": "Hyderabad, India",
            "salary": "₹7L - ₹9.5L PA",
            "apply_url": "https://careers.codetech.io/jobs/python-dev",
            "status": "interview",
            "date_applied": "2026-09-20",
            "followup_date": "2026-09-27",
            "interview_date": "2026-10-04",
            "notes": "Technical round completed. System design & SQL live coding scheduled."
        },
        {
            "id": "app_scout_03",
            "user_id": user_id,
            "company": "Scout Inc",
            "role": "Data Analyst",
            "location": "Hyderabad, India",
            "salary": "₹6.5L - ₹8.5L PA",
            "apply_url": "https://scoutinc.com/careers/data-analyst",
            "status": "applied",
            "date_applied": "2026-09-25",
            "followup_date": "2026-10-02",
            "notes": "Application submitted with tailored resume and cover pitch."
        },
        {
            "id": "app_globalcorp_04",
            "user_id": user_id,
            "company": "GlobalCorp",
            "role": "Junior Data Analyst",
            "location": "India (Remote)",
            "salary": "₹6L - ₹8L PA",
            "apply_url": "https://globalcorp.com/jobs/junior-data-analyst",
            "status": "saved",
            "date_applied": "2026-09-28",
            "followup_date": "",
            "notes": "High fit (68% match score). Tailoring resume for DAX & Snowflake focus."
        }
    ]

    for app in sample_applications:
        db_manager.save_application(app)
        print(f"✓ Seeded CRM Application: {app['role']} at {app['company']} [{app['status'].upper()}]")

    # 4. Seed Mock Interview History (`mock_interviews`)
    print("\n[4/4] Seeding Mock Interview History (`mock_interviews`)...")
    if db_manager.is_connected and db_manager.db is not None:
        mock_records = [
            {
                "user_id": user_id,
                "role": "Data Analyst",
                "company": "Microsoft",
                "question": "How do you handle missing values and outliers in a large dataset before feeding it into a BI dashboard or ML model?",
                "candidate_answer": "In my customer churn project, I used SQL queries with IS NULL and COALESCE to identify missing entries. For numerical columns, I analyzed IQR and replaced outliers with median values in Pandas, which improved dashboard accuracy.",
                "overall_score": 8.8,
                "rubric_scores": {
                    "technical_correctness": 8.8,
                    "structure_star": 9.0,
                    "relevance": 8.5,
                    "clarity": 8.8
                },
                "feedback": "Strong STAR structure and specific tool references (SQL COALESCE, Pandas IQR).",
                "created_at": "2026-09-28T14:30:00Z"
            },
            {
                "user_id": user_id,
                "role": "Data Analyst",
                "company": "Amazon",
                "question": "What is the difference between WHERE and HAVING in SQL?",
                "candidate_answer": "WHERE filters rows before aggregate calculations are applied, while HAVING filters grouped rows after the GROUP BY aggregation has been calculated.",
                "overall_score": 9.2,
                "rubric_scores": {
                    "technical_correctness": 9.5,
                    "structure_star": 9.0,
                    "relevance": 9.0,
                    "clarity": 9.3
                },
                "feedback": "Concise and technically precise distinction between row-level filtering and group aggregate filtering.",
                "created_at": "2026-09-29T11:15:00Z"
            }
        ]
        db_manager.db.mock_interviews.delete_many({"user_id": user_id})
        db_manager.db.mock_interviews.insert_many(mock_records)
        print(f"✓ Saved {len(mock_records)} mock interview scorecards to MongoDB.")

    print("\n" + "=" * 60)
    print("🎉 ALL MONGODB COLLECTIONS SUCCESSFULLY SEEDED & SYNCHRONIZED!")
    print("Database: ai_job_agent")
    print("Collections available in MongoDB Compass:")
    print("  • users")
    print("  • candidate_profiles")
    print("  • applications")
    print("  • mock_interviews")
    print("=" * 60)


if __name__ == "__main__":
    seed_database()
