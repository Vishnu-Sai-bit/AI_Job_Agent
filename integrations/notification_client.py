"""
==========================================================
Integrations - Notification Client
==========================================================
"""

from typing import Dict, Any

class NotificationClient:
    def push_alert(self, user_id: str, title: str, text: str) -> Dict[str, Any]:
        return {"user_id": user_id, "title": title, "delivered": True}

notification_client = NotificationClient()
