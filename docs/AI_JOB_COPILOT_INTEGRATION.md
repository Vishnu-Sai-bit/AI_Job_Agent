# 🤖 AI Job Copilot: Full Technical Documentation & Integration Guide

## 📌 1. Project Overview

**AI Job Copilot** is an enterprise career intelligence platform designed to streamline job discovery, resume optimization, and application tracking. Built with Python, modern web frontends, FastAPI, and robust local/cloud data stores, it provides automated skill extraction, ATS compatibility scoring, customized interview preparation, and tailored application document generation.

---

## 🏗️ 2. Architecture & Tech Stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit 1.58+ / Modern Vanilla HTML5, CSS3 Glassmorphic UI & JavaScript | Glassmorphic dark dashboard, interactive workflows, dynamic SVG gauges, real-time filters |
| **Data Parsing & NLP** | `pdfplumber`, PyMuPDF, Regular Expressions, Fuzzy matching | Extracts text, tokenizes skills, handles multi-column layouts, and evaluates resume structure |
| **Analytics & Scoring** | Custom Rule & Vector Matching, Pandas, NumPy | Computes ATS scores (0–100%), skill gaps, weighted compatibility, and job recommendation ranking |
| **Storage & Database** | SQLite 3 (`job_copilot.db`), MongoDB Atlas, JSON configurations | Stores jobs, candidate application tracking history (CRM), mock interview evaluations, and user settings |
| **Document Generation** | Dynamic Prompt Templating & Generative AI | Generates tailored resumes, cover letters, and cold recruiter outreach drafts |

---

## 📂 3. Directory Structure

```text
AI_Job_Copilot/
├── Config/                  # Application configuration & user preferences
│   ├── settings.py          # Settings manager
│   └── user_settings.json   # Target roles, locations, minimum ATS threshold
├── ai/                      # Core Intelligence Engines
│   ├── ats_score.py         # ATS scoring algorithm comparing candidate vs job
│   ├── skill_gap.py         # Matched vs missing skills & learning roadmaps
│   ├── job_matcher.py       # Candidate-job compatibility matching
│   ├── recommender.py       # Top job recommendations sorted by ATS score
│   ├── skill_extractor.py   # Token extractor from raw text
│   ├── resume_optimizer.py  # Resume feedback & optimization suggestions
│   ├── interview_questions.py # Technical & HR interview question bank
│   ├── cover_letter_ai.py   # Tailored cover letter generator
│   └── email_generator.py   # Tailored recruiter outreach generator
├── app/                     # Streamlit / Web Frontend Pages
│   ├── app.py               # Main navigation router & theme configuration
│   ├── home.py              # Landing hero banner & dashboard overview
│   ├── resume_page.py       # PDF resume upload & parsing
│   ├── resume_analysis_page.py # Skill breakdown & resume statistics
│   ├── jobs_page.py         # Job browser & keyword search
│   ├── ats_page.py          # Detailed ATS score & missing skill report
│   ├── recommendations_page.py # Ranked job recommendations
│   ├── cover_letter_page.py # Auto-generate and copy cover letters
│   ├── email_page.py        # Cold outreach email builder
│   ├── application_page.py  # Application tracker (Applied, Interview, Offer)
│   ├── interview_page.py    # Technical & behavioral interview preparation
│   ├── analytics_page.py    # Visual metrics on jobs and applications
│   └── settings_page.py     # User preferences manager
├── database/                # Database Storage
│   ├── job_copilot.db       # Primary SQLite database
│   ├── db_manager.py        # SQLite connection manager
│   ├── database.py          # Table initialization scripts
│   ├── application_tracker.py # CRUD operations for tracked applications
│   └── job_skills.py        # Skill mappings for primary technical roles
├── jobs/                    # Data Ingestion
│   ├── job_repository.py    # Data access layer for jobs
│   ├── job_loader.py        # Database populator & scraper integrations
│   └── india_jobs.py        # Curated technical jobs dataset
├── output/                  # Exports & Artifacts
│   ├── jobs_export.csv      # Exported jobs dataset (CSV)
│   └── jobs_export.json     # Exported jobs dataset (JSON)
├── resumes/                 # Resume sample storage
├── main.py                  # One-click startup runner
└── requirements.txt         # Project dependencies
```

---

## ⚙️ 4. How the Core Features Work

### 1. Resume Parsing (`ai/skill_extractor.py` & `app/resume_page.py`)
- Extracts text from uploaded PDFs using `pdfplumber` and PyMuPDF.
- Scans text against a dictionary of technical skills (`Python`, `SQL`, `AWS`, `Pandas`, `Power BI`, `Tableau`, `Excel`, etc.).
- Stores extracted skills and raw text into application state and candidate profile structures.

### 2. ATS Match Scoring (`ai/ats_score.py` & `ai/skill_gap.py`)
Compares candidate skills against job requirements:
$$\text{Score} = \left( \frac{\text{Count of Matched Skills}}{\text{Total Required Skills}} \right) \times 100$$

- **Matched Skills**: Skills present in both resume and job.
- **Missing Skills**: Critical skills required by the target role but absent in the resume.
- **Action Plan**: Automatically recommends curated learning roadmaps and hands-on portfolio projects for missing skills.

### 3. Application Tracker CRM (`database/application_tracker.py`)
Manages candidate pipelines across structured stages:
- **Fields**: `id`, `company`, `title`, `location`, `status` (`Applied`, `Assessment`, `Interview`, `Offer`, `Saved`), `applied_date`, `notes`.
- **Kanban Pipeline**: Visual drag-and-drop status distribution and follow-up reminders.

---

## 🔄 5. Sharing or Migrating Data into Another Project

### Option A: Using Exported CSV / JSON (Simplest)
The project's job dataset is exportable to the `output/` folder:
- **CSV Format**: `output/jobs_export.csv`
- **JSON Format**: `output/jobs_export.json`

**How to use in another Python/Pandas project:**
```python
import pandas as pd

# Load from CSV
jobs_df = pd.read_csv("jobs_export.csv")

# Or load from JSON
jobs_json_df = pd.read_json("jobs_export.json")
print(jobs_df.head())
```

### Option B: Sharing the SQLite Database File
Copy `database/job_copilot.db` directly into any other project. Any SQLite client or Python script can read it:
```python
import sqlite3

conn = sqlite3.connect("job_copilot.db")
cursor = conn.cursor()
cursor.execute("SELECT id, title, company, location, salary FROM jobs")
for row in cursor.fetchall():
    print(row)
conn.close()
```

### Option C: Reusing the AI Modules as a Library
The `ai/` folder is modular and decoupled from any specific UI framework. You can import and reuse it in FastAPI, Django, Flask, CLI scripts, or microservices:

```python
from ai.ats_score import ATSScore
from ai.skill_gap import SkillGap

candidate_skills = ["Python", "SQL", "Pandas"]
job_skills = ["Python", "SQL", "Power BI", "Tableau"]

gap_analyzer = SkillGap()
gap_result = gap_analyzer.analyze_gap(candidate_skills, job_skills)

print("Match Score:", gap_result["match_percentage"])
print("Missing Skills:", gap_result["missing_skills"])
```
