"""
==========================================================
AI JobAgent - Google SMTP (Gmail) Email Delivery Service
Author : Beere Vishnu Sai
Description:
    Dispatches transactional emails (Password Reset OTP,
    Welcome Onboarding, Job Alerts) using Gmail SMTP (smtp.gmail.com).
==========================================================
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple, Optional
from utils.logger import logger


class GmailSMTPService:
    """
    Gmail SMTP client supporting TLS authentication and responsive HTML templates.
    """

    @property
    def server_host(self) -> str:
        return os.getenv("MAIL_SERVER", "smtp.gmail.com")

    @property
    def port(self) -> int:
        return int(os.getenv("MAIL_PORT", "587"))

    @property
    def username(self) -> str:
        return os.getenv("GMAIL_USER") or os.getenv("MAIL_USERNAME", "")

    @property
    def password(self) -> str:
        return os.getenv("GMAIL_APP_PASSWORD") or os.getenv("MAIL_PASSWORD", "")

    @property
    def sender_name(self) -> str:
        return os.getenv("MAIL_SENDER_NAME", "AI JobAgent")

    def is_configured(self) -> bool:
        """Check if Gmail SMTP credentials are configured in environment."""
        return bool(self.username and self.password)

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Send an email via Google SMTP with TLS.
        Returns (success: bool, status_message: str).
        """
        if not self.is_configured():
            msg = (
                f"[SIMULATION] Gmail SMTP not configured (set GMAIL_USER and GMAIL_APP_PASSWORD in .env). "
                f"Subject: '{subject}' -> Recipient: {to_email}"
            )
            logger.info(msg)
            return False, "Gmail SMTP credentials not configured. Using local dispatch."

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.sender_name} <{self.username}>"
            msg["To"] = to_email

            if text_body:
                msg.attach(MIMEText(text_body, "plain", "utf-8"))
            if html_body:
                msg.attach(MIMEText(html_body, "html", "utf-8"))

            with smtplib.SMTP(self.server_host, self.port, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                # Clean app password of spaces (Google displays app passwords in 4x4 format)
                clean_password = self.password.replace(" ", "")
                server.login(self.username, clean_password)
                server.send_message(msg)

            logger.info(f"Email successfully delivered to {to_email} via Gmail SMTP.")
            return True, f"Email delivered to {to_email}."
        except smtplib.SMTPAuthenticationError as e:
            err = f"Gmail SMTP Authentication failed. Check your App Password: {e}"
            logger.error(err)
            return False, err
        except Exception as e:
            err = f"Failed to send email via Gmail SMTP: {e}"
            logger.error(err)
            return False, err

    def send_password_reset_otp(self, to_email: str, otp_code: str, user_name: str = "Candidate") -> Tuple[bool, str]:
        """
        Send a 6-digit OTP verification email for password reset.
        """
        subject = f"Your Verification Code: {otp_code} - AI JobAgent"
        
        text_body = f"""Hello {user_name},

Your verification code for AI JobAgent password reset is:

    {otp_code}

This code will expire in 15 minutes. If you did not request this, you can safely ignore this email.

Best regards,
The AI JobAgent Team
https://ai-job-agent-kna8.onrender.com
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; margin: 0; padding: 24px; color: #e2e8f0; }}
    .card {{ max-width: 520px; margin: 0 auto; background: #131b2e; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .header {{ background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%); padding: 32px 24px; text-align: center; }}
    .header h1 {{ margin: 0; color: #ffffff; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
    .header p {{ margin: 6px 0 0 0; color: rgba(255,255,255,0.85); font-size: 14px; }}
    .content {{ padding: 32px 24px; }}
    .greeting {{ font-size: 16px; color: #cbd5e1; margin-bottom: 16px; }}
    .message {{ font-size: 14px; color: #94a3b8; line-height: 1.6; margin-bottom: 24px; }}
    .otp-box {{ background: #0f172a; border: 2px dashed #6366f1; border-radius: 12px; padding: 20px; text-align: center; margin: 24px 0; }}
    .otp-code {{ font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #818cf8; font-family: monospace; }}
    .expiry {{ font-size: 12px; color: #64748b; margin-top: 8px; }}
    .footer {{ padding: 20px 24px; text-align: center; background: #0a0f1d; border-top: 1px solid #1e293b; font-size: 12px; color: #64748b; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1>AI JobAgent</h1>
      <p>Account Security & Verification</p>
    </div>
    <div class="content">
      <div class="greeting">Hello {user_name},</div>
      <div class="message">
        We received a request to reset your password or verify your Gmail account on AI JobAgent. Use the one-time code below to complete the verification:
      </div>
      <div class="otp-box">
        <div class="otp-code">{otp_code}</div>
        <div class="expiry">Valid for 15 minutes &bull; Do not share with anyone</div>
      </div>
      <div class="message">
        If you did not initiate this request, you can safely disregard this email. Your account remains completely secure.
      </div>
    </div>
    <div class="footer">
      AI JobAgent &bull; Next-Gen Career Intelligence Platform<br>
      <a href="https://ai-job-agent-kna8.onrender.com" style="color: #818cf8; text-decoration: none;">ai-job-agent-kna8.onrender.com</a>
    </div>
  </div>
</body>
</html>
"""
        return self.send_email(to_email, subject, html_body, text_body)

    def send_welcome_email(self, to_email: str, user_name: str = "Candidate") -> Tuple[bool, str]:
        """
        Send a welcome email upon registration or Google SSO signup.
        """
        subject = f"Welcome to AI JobAgent, {user_name}!"
        text_body = f"""Hello {user_name},

Welcome to AI JobAgent! Your account is now active.

Get started with:
- 6-Dimension ATS Resume Auditing
- Live Multi-Portal Job Matching
- AI Mock Interview Simulation
- Kanban Application Tracking

Visit your dashboard: https://ai-job-agent-kna8.onrender.com/dashboard

Best regards,
The AI JobAgent Team
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0b0f19; margin: 0; padding: 24px; color: #e2e8f0; }}
    .card {{ max-width: 520px; margin: 0 auto; background: #131b2e; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; }}
    .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 32px 24px; text-align: center; color: white; }}
    .content {{ padding: 32px 24px; }}
    .btn {{ display: inline-block; background: #6366f1; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0; }}
    .footer {{ padding: 16px 24px; text-align: center; background: #0a0f1d; font-size: 12px; color: #64748b; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1 style="margin:0;">Welcome to AI JobAgent</h1>
      <p style="margin:4px 0 0 0; opacity:0.9;">Career Intelligence & Job Automation</p>
    </div>
    <div class="content">
      <p>Hello <strong>{user_name}</strong>,</p>
      <p>Your account has been successfully created. You now have full access to our comprehensive suite of career acceleration tools:</p>
      <ul>
        <li><strong>ATS Resume Auditing</strong> &mdash; 6-dimension evaluation</li>
        <li><strong>Multi-Board Job Discovery</strong> &mdash; Real-time listings</li>
        <li><strong>Simulated Mock Interviews</strong> &mdash; Instant AI grading</li>
        <li><strong>Application Kanban CRM</strong> &mdash; Pipeline tracking</li>
      </ul>
      <div style="text-align: center;">
        <a href="https://ai-job-agent-kna8.onrender.com/dashboard" class="btn">Launch Your Dashboard</a>
      </div>
    </div>
    <div class="footer">
      AI JobAgent &bull; <a href="https://ai-job-agent-kna8.onrender.com" style="color:#818cf8;">ai-job-agent-kna8.onrender.com</a>
    </div>
  </div>
</body>
</html>
"""
        return self.send_email(to_email, subject, html_body, text_body)


# Global singleton instance
gmail_service = GmailSMTPService()
