import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.resume_parser import extract_resume_text
from services.resume_analyzer import analyze_resume

pdf_path = Path("resumes/Beere_Vishnu_Sai_Resume.pdf")
print("Reading PDF:", pdf_path)
text = extract_resume_text(pdf_path)
resume = analyze_resume(text)

print("\n--- Parsed Resume Data ---")
print("Preferred Role:", resume.preferred_role)
print("Skills:", resume.skills)
print("Preferred Location:", resume.preferred_location)
print("Experience Years:", resume.experience_years)
