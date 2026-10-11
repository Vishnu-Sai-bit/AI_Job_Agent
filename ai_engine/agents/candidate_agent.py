"""
==========================================================
AI Engine Agent - Candidate Agent
==========================================================
"""

from typing import Dict, Any

class CandidateAgent:
    """Constructs structured candidate profiles from extracted signals."""
    
    def process_profile(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": parsed_data.get("name", "Candidate"),
            "skills": parsed_data.get("skills", []),
            "experience_years": parsed_data.get("experience_years", 0),
            "status": "ready"
        }

candidate_agent = CandidateAgent()
