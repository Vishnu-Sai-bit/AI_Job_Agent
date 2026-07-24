import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.search_jobs import search_jobs
from models import ResumeData

resume = ResumeData(
    name="Beere Vishnu Sai",
    skills=["Python", "SQL", "Tableau"],
    preferred_role="Data Analyst",
    preferred_location="Hyderabad",
    experience_years=0.5
)

print("Starting job search to test file exporter...")
result = search_jobs(resume)
print("Search status:", result.status)

report_file = Path("matched_jobs.md")
if report_file.exists():
    print("\n--- matched_jobs.md generated successfully! ---")
    print(report_file.read_text(encoding="utf-8")[:600])
else:
    print("\nError: matched_jobs.md was NOT generated.")
