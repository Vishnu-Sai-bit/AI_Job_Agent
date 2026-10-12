"""
==========================================================
AI Job Copilot - Notification Service
==========================================================
"""

from typing import List, Dict, Any

class NotificationService:
    @staticmethod
    def notify_user(title: str, message: str, category: str = "general") -> Dict[str, Any]:
        return {
            "title": title,
            "message": message,
            "category": category,
            "status": "delivered"
        }

notification_service = NotificationService()
