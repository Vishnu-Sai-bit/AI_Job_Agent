"""
==========================================================
AI JobAgent - Report Generator Service
Author : Antigravity
==========================================================
"""

import datetime
from typing import Dict, Any, List

def generate_profile_report(resume_data: Dict[str, Any], ats_report: Dict[str, Any]) -> str:
    """
    Generate a complete formatted markdown report for the candidate.
    """
    name = resume_data.get("name") or "CANDIDATE"
    preferred_role = resume_data.get("preferred_role") or "Data Analyst"
    ats_score = ats_report.get("ats_score") or 0.0
    
    report_md = []
    report_md.append(f"# 📊 AI JobAgent Career Suitability Report")
    report_md.append(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_md.append(f"**Candidate Name:** {name.upper()}")
    report_md.append(f"**Target Role:** {preferred_role.upper()}")
    report_md.append(f"**ATS Compatibility Rating:** {ats_score}%")
    report_md.append("\n---")
    
    # Skills Section
    report_md.append("## 🔑 Extracted Technical Stack")
    skills = resume_data.get("skills", [])
    if skills:
        report_md.append(", ".join([f"`{s}`" for s in skills]))
    else:
        report_md.append("No skills extracted.")
    report_md.append("")
    
    # ATS Feedback
    report_md.append("## 📈 ATS Analysis & Suggestions")
    for category, feedback in ats_report.get("feedback", {}).items():
        report_md.append(f"### 🎯 {category.title()}")
        report_md.append(f"- **Impact Rating:** {feedback.get('score', 0)}/10")
        report_md.append(f"- **AI Advice:** {feedback.get('reason', 'N/A')}")
        report_md.append("")
        
    return "\n".join(report_md)
