"""
==========================================================
AI Engine Agent - Assistant Agent
==========================================================
"""

from typing import Dict, Any, Optional

class AssistantAgent:
    """Answers candidate career questions grounded in context."""

    def answer_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        from services.analytics.copilot_assistant import copilot_assistant
        return copilot_assistant.answer_query(query, resume_context=context)

assistant_agent = AssistantAgent()
