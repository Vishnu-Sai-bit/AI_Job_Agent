import re
from typing import Dict, Any, List

ACTION_VERBS = [
    "spearheaded", "architected", "engineered", "implemented", "developed", "designed",
    "optimized", "scaled", "automated", "reduced", "increased", "boosted", "delivered",
    "led", "managed", "deployed", "refactored", "built", "accelerated", "resolved"
]

class ResumeAnalyzer:
    def analyze_resume_quality(self, raw_text: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates resume readability, completeness, impact metrics, and ATS formatting structure.
        Returns a quality report with scores and actionable improvement recommendations.
        """
        readability_score, readability_feedback = self._evaluate_readability(raw_text)
        completeness_score, missing_sections = self._evaluate_completeness(parsed_data)
        impact_score, impact_feedback = self._evaluate_impact_and_metrics(raw_text)
        formatting_score, formatting_feedback = self._evaluate_formatting(raw_text)

        # Overall Resume Quality Score (0-100)
        overall_quality = round(
            0.30 * readability_score +
            0.35 * completeness_score +
            0.20 * impact_score +
            0.15 * formatting_score,
            1
        )

        all_feedback = []
        all_feedback.extend(readability_feedback)
        if missing_sections:
            all_feedback.append(f"Consider adding or detailing sections for: {', '.join(missing_sections)}.")
        all_feedback.extend(impact_feedback)
        all_feedback.extend(formatting_feedback)

        return {
            "overall_quality_score": overall_quality,
            "readability_score": readability_score,
            "completeness_score": completeness_score,
            "impact_score": impact_score,
            "formatting_score": formatting_score,
            "missing_sections": missing_sections,
            "actionable_feedback": all_feedback,
            "skills_count": len(parsed_data.get("skills", [])),
            "experience_years": parsed_data.get("experience_years", 0)
        }

    def _evaluate_readability(self, text: str) -> (float, List[str]):
        words = text.split()
        word_count = len(words)
        feedback = []

        if word_count < 150:
            return 40.0, ["Resume is very brief. Expand on your project accomplishments and responsibilities."]
        elif word_count > 1200:
            return 70.0, ["Resume is on the longer side. Aim for a concise 1-2 page presentation (400-800 words)."]
        
        score = 90.0
        # Check average word length or sentence length
        lines = [l for l in text.split("\n") if l.strip()]
        if len(lines) > 0 and (word_count / len(lines)) > 25:
            score -= 10
            feedback.append("Some sentences appear long and dense. Use shorter bullet points for clarity.")
        
        return max(score, 50.0), feedback

    def _evaluate_completeness(self, data: Dict[str, Any]) -> (float, List[str]):
        missing = []
        score = 100.0

        if not data.get("email"):
            missing.append("Email Address")
            score -= 15
        if not data.get("phone"):
            missing.append("Phone Number")
            score -= 10
        if not data.get("skills") or len(data.get("skills", [])) < 3:
            missing.append("Skills List")
            score -= 25
        if not data.get("experience") and data.get("experience_years", 0) == 0:
            missing.append("Work Experience")
            score -= 25
        if not data.get("education"):
            missing.append("Education")
            score -= 15
        if not data.get("projects"):
            missing.append("Projects")
            score -= 10

        return max(score, 20.0), missing

    def _evaluate_impact_and_metrics(self, text: str) -> (float, List[str]):
        lowered = text.lower()
        feedback = []
        
        # Check action verbs
        action_verb_count = sum(1 for verb in ACTION_VERBS if verb in lowered)
        
        # Check metrics/percentages/numbers (quantifiable results)
        metric_matches = re.findall(r"(\b\d+%\b|\$\d+[\w]*|\b\d+x\b|\b\d{2,}\+?\b)", text)
        metric_count = len(metric_matches)

        score = 50.0
        score += min(action_verb_count * 5, 25.0)
        score += min(metric_count * 5, 25.0)

        if action_verb_count < 3:
            feedback.append("Use strong action verbs (e.g., 'Architected', 'Engineered', 'Optimized') at the start of bullet points.")
        if metric_count < 2:
            feedback.append("Include quantifiable achievements (e.g., 'reduced latency by 35%', 'handled 10k+ daily users').")

        return min(score, 100.0), feedback

    def _evaluate_formatting(self, text: str) -> (float, List[str]):
        score = 85.0
        feedback = []
        
        # Check bullet points
        bullet_count = text.count("*") + text.count("-") + text.count("•")
        if bullet_count < 5:
            score -= 15
            feedback.append("Structure roles and project details with bullet points for higher ATS parsing accuracy.")

        return max(score, 50.0), feedback
