# AI Job Agent — Career Intelligence & Verified Application Assistant

AI Job Agent is a Python + Flask platform designed to revolutionize the job application lifecycle. Unlike traditional job boards that rely solely on keyword queries or send candidates to dead-end homepages, AI Job Agent understands candidate resumes, collects real job openings from verified platforms worldwide, calculates transparent job-specific ATS compatibility scores, and guarantees that every **Apply Now** button leads directly to that position's genuine official application page.

---

## Key Core Guarantees

1. **100% Grounded in Real Sources**: Every recommended job originates from a traceable, verified source record (Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Workable, Recruitee, Remotive, RemoteOK, Arbeitnow, or official company career portals).
2. **Direct Official Application Links**: The `/apply/<job_id>` route retrieves the verified application URL from the database and validates scheme, SSRF safety, and permitted hosts before safely redirecting. It never fabricates URLs or relies on open query redirects.
3. **Transparent ATS Scoring**: Implements an explainable, deterministic weighted compatibility formula:
   $$\mathbf{M = 0.40S + 0.25E + 0.15K + 0.10P + 0.10Q}$$
   - **S (40%)**: Required & Preferred Skill Overlap
   - **E (25%)**: Relevant Experience Alignment
   - **K (15%)**: Job-Description Keyword Coverage (TF-IDF Cosine Similarity)
   - **P (10%)**: Project Evidence Overlap
   - **Q (10%)**: Qualification & Degree Alignment
   *(Location & Work Mode fit is preserved as an informative eligibility flag for user transparency without skewing core ATS qualifications)*.
4. **Conversational Career Assistant**: Natural language career queries (e.g. *"Find Python developer jobs matching my resume"*, *"Show jobs with an 80% or higher match"*, *"Which skills am I missing?"*, *"Prepare a cover letter"*).
5. **Human-in-the-Loop Privacy & Safety**: Resumes are stored outside public web directories. Clicking Apply Now never automatically marks a job as applied—applications are tracked accurately through candidate confirmation or verified integration.

---

## Project Structure

```
d:\vishnu\JOB\
├── app.py                     # Flask application factory
├── config.py                  # Configurations (Dev, Testing, Prod)
├── extensions.py              # SQLAlchemy, Migrate, LoginManager
├── requirements.txt           # Core Python dependencies
├── .env.example               # Environment variables template
├── models/                    # Database models
│   ├── user.py                # User & CandidateProfile
│   ├── resume.py              # Resume (raw text, parsed data, ATS scores)
│   ├── job_source.py          # Platform & company board configurations
│   ├── job.py                 # Grounded Job listings & VerificationLog
│   ├── job_match.py           # JobMatch & SavedJob
│   └── application.py         # Application tracker & documents
├── collectors/                # Independent platform connectors
│   ├── base_collector.py      # Pydantic schemas & BaseCollector
│   ├── greenhouse_collector.py
│   ├── lever_collector.py
│   ├── ashby_collector.py
│   ├── workday_collector.py   # Workday adapter
│   ├── remotive_collector.py
│   ├── remoteok_collector.py
│   ├── arbeitnow_collector.py
│   └── company_careers_collector.py
├── services/                  # Business logic
│   ├── resume_parser.py       # PDF/DOCX contact, skill, experience extractor
│   ├── resume_analyzer.py     # Readability, completeness, impact audit
│   ├── ats_scorer.py          # Resume quality score and tiered diagnostic
│   ├── job_normalizer.py      # Schema mapping, URL cleaning, skill extraction
│   ├── job_deduplicator.py    # Multi-factor & fuzzy deduplication
│   ├── job_verifier.py        # Safe link verification & SSRF defense
│   ├── job_matcher.py         # Explainable weighted matching engine
│   ├── job_search_service.py  # Filtered job discovery & pagination
│   ├── application_service.py # Kanban application pipeline management
│   ├── cover_letter_service.py# Grounded cover letter & interview Q&A
│   └── career_assistant.py    # Conversational natural language agent
├── routes/                    # Modular Flask blueprints
│   ├── auth_routes.py         # /login, /register, /logout
│   ├── dashboard_routes.py    # /, /dashboard, /settings
│   ├── resume_routes.py       # /resume/upload, /resume/analysis
│   ├── ats_routes.py          # /ats, /ats/job/<job_id>
│   ├── job_routes.py          # /jobs, /jobs/<job_id>, /apply/<job_id>
│   ├── application_routes.py  # /applications, /applications/prepare/<job_id>
│   └── assistant_routes.py    # /assistant, /assistant/api/chat
├── tasks/                     # Async data pipelines
│   ├── refresh_jobs.py        # Periodic collection & normalization
│   ├── verify_job_links.py    # Background link and status re-verification
│   └── recompute_matches.py   # Deterministic match computation
├── utils/                     # Security & validation helpers
│   ├── file_validation.py     # PDF/DOCX header magic bytes & size check
│   ├── url_validation.py      # SSRF defense, host & scheme validation
│   ├── text_extraction.py     # PyMuPDF & python-docx extractors
│   ├── security.py            # Open redirect defense & ownership checks
│   └── logging_config.py
├── templates/                 # Bootstrap 5 responsive templates
├── static/                    # Custom CSS & JavaScript
└── tests/                     # Automated pytest suite
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Virtual environment (`.venv`)

### 2. Installation
```powershell
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Automated Tests
```powershell
pytest -v
```

### 4. Start the Application
```powershell
python app.py
```
Open your browser at `http://127.0.0.1:5000`.
