"""
==========================================================
AI JobAgent - FastAPI Backend
Author : Beere Vishnu Sai

Description:
    REST API for AI JobAgent.
==========================================================
"""

from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
)

from fastapi.middleware.cors import CORSMiddleware

from config import (
    APP_NAME,
    VERSION,
    API_DESCRIPTION,
    ALLOWED_ORIGINS,
    RESUME_FOLDER,
    SUPPORTED_RESUME_FORMATS,
    MAX_RESUME_SIZE_MB,
)

from models import ResumeData
from services import (
    extract_resume_text,
    analyze_resume,
    calculate_ats,
    search_jobs,
    search_statistics,
    optimize_resume,
    generate_cover_letter,
    generate_interview_questions,
    generate_learning_roadmap,
    predict_salary,
    optimize_linkedin_profile,
    generate_job_emails,
    generate_profile_report,
)
from pydantic import BaseModel
from typing import List, Optional

# ==========================================================
# Pydantic Schemas for Additional Services
# ==========================================================

class CoverLetterRequest(BaseModel):
    name: str
    skills: List[str]
    job_title: str
    company: str
    job_desc: Optional[str] = ""

class InterviewRequest(BaseModel):
    role: str
    skills: List[str]
    resume_context: Optional[str] = ""
    question_count: Optional[int] = 5
    interviewer_role: Optional[str] = "Senior Technical Recruiter"

class RoadmapRequest(BaseModel):
    role: str
    skills: List[str]

class SalaryRequest(BaseModel):
    role: str
    experience_years: float
    skills: List[str]
    location: str

class LinkedInRequest(BaseModel):
    name: str
    role: str
    skills: List[str]
    experience_text: Optional[str] = ""

class EmailRequest(BaseModel):
    name: str
    skills: List[str]
    role: str
    company: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""
    resume_context: Optional[str] = ""

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description=API_DESCRIPTION,
)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Helper Functions
# ==========================================================

def validate_resume_file(file: UploadFile):
    """
    Validate uploaded resume.
    """

    extension = Path(file.filename).suffix.lower()

    if extension not in SUPPORTED_RESUME_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported resume format: {extension}",
        )


async def save_resume(file: UploadFile) -> Path:
    """
    Save uploaded resume.
    """

    validate_resume_file(file)

    content = await file.read()

    size_mb = len(content) / (1024 * 1024)

    if size_mb > MAX_RESUME_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum resume size is {MAX_RESUME_SIZE_MB} MB.",
        )

    destination = RESUME_FOLDER / file.filename

    with open(destination, "wb") as f:
        f.write(content)

    return destination

# ==========================================================
# Home
# ==========================================================

@app.get("/", tags=["Home"])
def root():

    return {
        "application": APP_NAME,
        "version": VERSION,
        "status": "Running",
        "author": "Beere Vishnu Sai",
    }

# ==========================================================
# Health
# ==========================================================

@app.get("/health", tags=["Health"])
def health():

    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": VERSION,
    }

# ==========================================================
# Info
# ==========================================================

@app.get("/info", tags=["Information"])
def info():

    return {
        "application": APP_NAME,
        "version": VERSION,
        "description": API_DESCRIPTION,
        "documentation": "/docs",
    }

# ==========================================================
# Upload Resume
# ==========================================================

@app.post("/upload-resume", tags=["Resume"])
async def upload_resume(
    file: UploadFile = File(...),
):

    destination = await save_resume(file)

    return {

        "success": True,

        "filename": destination.name,

        "path": str(destination),

        "message": "Resume uploaded successfully.",

    }

# ==========================================================
# Analyze Resume
# ==========================================================

@app.post("/analyze-resume", tags=["Resume"])
async def analyze_uploaded_resume(
    file: UploadFile = File(...),
):
    try:
        destination = await save_resume(file)
        resume_text = extract_resume_text(destination)
        resume: ResumeData = analyze_resume(resume_text)
        job_result = search_jobs(resume)

        return {
            "success": True,
            "resume": resume.to_dict(),
            "result": job_result.to_dict(),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

# ==========================================================
# ATS Score
# ==========================================================

@app.post(
    "/ats-score",
    tags=["ATS"],
)
async def calculate_resume_ats(
    file: UploadFile = File(...),
):
    """
    Calculate ATS score for a resume.
    """

    try:

        destination = await save_resume(file)

        resume_text = extract_resume_text(
            destination
        )

        resume: ResumeData = analyze_resume(
            resume_text
        )

        ats = calculate_ats(
            resume
        )

        return {

            "success": True,

            "ats_score": ats,

            "resume": resume.to_dict(),

        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),

        )
    
# ==========================================================
# Search Jobs
# ==========================================================

@app.post(
    "/search-jobs",
    tags=["Jobs"],
)
async def search_matching_jobs(
    file: UploadFile = File(...),
):
    """
    Analyze resume and search matching jobs.
    """

    try:

        destination = await save_resume(file)

        resume_text = extract_resume_text(
            destination
        )

        resume: ResumeData = analyze_resume(
            resume_text
        )

        result = search_jobs(
            resume
        )

        return {

            "success": True,

            "result": result.to_dict(),

        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),

        )
    
# ==========================================================
# Search Statistics
# ==========================================================

@app.post(
    "/search-statistics",
    tags=["Jobs"],
)
async def job_statistics(
    file: UploadFile = File(...),
):
    """
    Return job search statistics.
    """

    try:

        destination = await save_resume(file)

        resume_text = extract_resume_text(
            destination
        )

        resume: ResumeData = analyze_resume(
            resume_text
        )

        result = search_jobs(
            resume
        )

        stats = search_statistics(
            result.jobs
        )

        return {

            "success": True,

            "statistics": stats,

        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),

        )
    
# ==========================================================
# Optimize Resume
# ==========================================================

@app.post("/optimize-resume", tags=["Resume"])
async def optimize_uploaded_resume(
    file: UploadFile = File(...),
    target_role: str = None,
):
    """
    Optimize career summary, bullet points, action verbs, and skills.
    """
    try:
        destination = await save_resume(file)
        resume_text = extract_resume_text(destination)

        # If target_role is not provided, try to infer it
        if not target_role:
            from services.resume.resume_enricher import infer_role
            target_role = infer_role(resume_text)

        result = optimize_resume(resume_text, target_role)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# Additional Candidate Services Endpoints
# ==========================================================

@app.post("/generate-cover-letter")
def api_generate_cover_letter(req: CoverLetterRequest):
    """
    Generate a cover letter tailored for a specific candidate and job posting.
    """
    try:
        return generate_cover_letter(
            req.name,
            req.skills,
            req.job_title,
            req.company,
            req.job_desc
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-interview-questions")
def api_generate_interview_questions(req: InterviewRequest):
    """
    Generate mock technical/behavioral interview questions with tips and sample answers.
    """
    try:
        return generate_interview_questions(
            req.role,
            req.skills,
            req.resume_context,
            req.question_count,
            req.interviewer_role
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-learning-roadmap")
def api_generate_learning_roadmap(req: RoadmapRequest):
    """
    Generate a roadmap, cert suggestions, courses, and project ideas to bridge skill gaps.
    """
    try:
        return generate_learning_roadmap(req.role, req.skills)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-salary")
def api_predict_salary(req: SalaryRequest):
    """
    Estimate compensation ranges for both India (INR) and Remote international markets (USD).
    """
    try:
        return predict_salary(
            req.role,
            req.experience_years,
            req.skills,
            req.location
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-linkedin")
def api_optimize_linkedin(req: LinkedInRequest):
    """
    Optimize LinkedIn Headlines, About Summary, bullet tips, and SEO keywords.
    """
    try:
        return optimize_linkedin_profile(
            req.name,
            req.role,
            req.skills,
            req.experience_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-emails")
def api_generate_emails(req: EmailRequest):
    """
    Generate cold outreach, LinkedIn InMail, follow-up, and application templates.
    """
    try:
        return generate_job_emails(
            req.name,
            req.skills,
            req.role,
            req.company,
            req.email,
            req.phone,
            req.linkedin,
            req.github,
            req.portfolio,
            req.resume_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================================
# Global Exception Handler
# ==========================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request,
    exc,
):

    return {

        "success": False,

        "message": str(exc),

    }

# ==========================================================
# Run
# ==========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "app:app",

        host="0.0.0.0",

        port=8000,

        reload=True,

    )