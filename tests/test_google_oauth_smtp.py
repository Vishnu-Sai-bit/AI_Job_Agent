"""
==========================================================
AI JobAgent - Google OAuth, Gmail SMTP & JWT Test Suite
Author : Beere Vishnu Sai
==========================================================
"""

import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from app.extensions import db
from app.models.user import User
from services.auth.google_oauth import google_oauth
from services.email.gmail_smtp import gmail_service
from services.auth.auth_service import AuthService


class TestGoogleOAuthAndSMTP(unittest.TestCase):
    """Test suite for Google OAuth 2.0, Gmail SMTP, and signed JWT authentication."""

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_google_oauth_configuration(self):
        """Verify Google OAuth 2.0 client ID and secret are configured."""
        self.assertTrue(google_oauth.is_configured())
        self.assertIn("apps.googleusercontent.com", google_oauth.client_id)
        self.assertTrue(len(google_oauth.client_secret) > 10)

    def test_02_google_oauth_authorization_url(self):
        """Verify Google OAuth authorization URL contains mandatory parameters."""
        redirect_uri = "https://ai-job-agent-kna8.onrender.com/auth/google/callback"
        auth_url = google_oauth.get_authorization_url(redirect_uri)
        self.assertIn("accounts.google.com/o/oauth2/v2/auth", auth_url)
        self.assertIn("response_type=code", auth_url)
        self.assertIn("openid+email+profile", auth_url)
        self.assertIn("client_id=", auth_url)

    def test_03_gmail_smtp_configuration(self):
        """Verify Gmail SMTP server host, port, and credentials."""
        self.assertTrue(gmail_service.is_configured())
        self.assertEqual(gmail_service.server_host, "smtp.gmail.com")
        self.assertEqual(gmail_service.port, 587)
        self.assertEqual(gmail_service.username, "aijobagentofficial@gmail.com")
        self.assertEqual(len(gmail_service.password), 16)  # App password is 16 chars

    def test_04_jwt_generation_and_verification(self):
        """Verify JWT session creation, signature validation, and payload preservation."""
        token = AuthService.generate_token(
            user_id="usr_test_jwt",
            email="candidate@example.com",
            name="Test Candidate",
            role="candidate",
            auth_provider="google"
        )
        self.assertTrue(token)
        payload = AuthService.verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "usr_test_jwt")
        self.assertEqual(payload["email"], "candidate@example.com")
        self.assertEqual(payload["auth_provider"], "google")

    def test_05_google_callback_cancelled_code(self):
        """Verify Google OAuth callback handles user cancellation cleanly with redirect (no 500)."""
        response = self.client.get("/auth/google/callback?error=access_denied", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login", response.location)

    @patch("services.auth.google_oauth.GoogleOAuthService.exchange_code_for_user_info")
    def test_06_google_callback_exchange_failure(self, mock_exchange):
        """Verify Google OAuth callback handles code exchange errors without raising 500."""
        mock_exchange.return_value = (False, None, "Invalid authorization code")
        response = self.client.get("/auth/google/callback?code=bad_test_code", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login", response.location)

    @patch("services.auth.google_oauth.GoogleOAuthService.exchange_code_for_user_info")
    def test_07_google_callback_success(self, mock_exchange):
        """Verify Google OAuth callback succeeds, creates user, issues JWT, and redirects to dashboard."""
        mock_exchange.return_value = (
            True,
            {
                "email": "vishnu.test.oauth@gmail.com",
                "name": "Beere Vishnu Sai Test",
                "picture": "https://lh3.googleusercontent.com/test-pic.png",
                "google_id": "goog_test_987654",
            },
            "Google authentication successful."
        )
        response = self.client.get("/auth/google/callback?code=valid_test_code", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.location)

        # Verify user was created in DB
        user = User.query.filter_by(email="vishnu.test.oauth@gmail.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.full_name, "Beere Vishnu Sai Test")
        self.assertEqual(user.auth_provider, "google")

        # Verify JWT cookie was set
        cookie = response.headers.get("Set-Cookie", "")
        self.assertIn("jwt_token=", cookie)

    def test_08_me_endpoint_with_jwt(self):
        """Verify /auth/me returns user profile when provided valid JWT token."""
        token = AuthService.generate_token(
            user_id="usr_profile_me",
            email="me@jobagent.ai",
            name="Profile Tester",
            role="candidate",
            auth_provider="google"
        )
        response = self.client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["authenticated"])
        self.assertEqual(data["user"]["email"], "me@jobagent.ai")


if __name__ == "__main__":
    unittest.main()
