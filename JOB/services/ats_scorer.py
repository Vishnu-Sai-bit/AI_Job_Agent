from typing import Dict, Any
from services.resume_analyzer import ResumeAnalyzer

class ATSScorer:
    def __init__(self):
        self.analyzer = ResumeAnalyzer()

    def score_resume(self, raw_text: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes overall resume quality score and detailed diagnostic report.
        """
        analysis = self.analyzer.analyze_resume_quality(raw_text, parsed_data)
        
        # Determine performance tier
        overall = analysis["overall_quality_score"]
        if overall >= 85:
            tier = "Excellent"
            summary = "Your resume is well-structured, keyword-rich, and clearly details your technical impact."
        elif overall >= 70:
            tier = "Strong"
            summary = "Your resume meets standard ATS criteria with good clarity, but could benefit from more quantifiable achievements."
        elif overall >= 55:
            tier = "Moderate"
            summary = "Your resume conveys key skills, but lacks detail in key sections or formatting readability."
        else:
            tier = "Needs Improvement"
            summary = "Key resume sections are missing or brief. Expanding on technical skills and work experience is recommended."

        return {
            "overall_score": overall,
            "tier": tier,
            "summary": summary,
            "breakdown": {
                "readability": analysis["readability_score"],
                "completeness": analysis["completeness_score"],
                "impact_and_metrics": analysis["impact_score"],
                "structure_and_format": analysis["formatting_score"]
            },
            "actionable_feedback": analysis["actionable_feedback"],
            "missing_sections": analysis["missing_sections"]
        }
