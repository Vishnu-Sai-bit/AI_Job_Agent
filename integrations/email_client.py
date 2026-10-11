"""
==========================================================
Integrations - Email Client
==========================================================
"""

from typing import Dict, Any

class EmailClient:
    def send_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        # SMTP / SendGrid / Postmark driver
        return {"status": "sent", "recipient": recipient, "subject": subject}

email_client = EmailClient()
