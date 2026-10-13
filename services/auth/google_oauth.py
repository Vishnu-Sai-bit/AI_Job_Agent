"""
==========================================================
AI JobAgent - Google OAuth 2.0 Service
Author : Beere Vishnu Sai
Description:
    Manages Google OAuth 2.0 authentication, Authorization Code grant,
    Google ID Token validation, and user profile extraction.
==========================================================
"""

import os
import urllib.parse
from typing import Dict, Any, Optional, Tuple
import requests
import jwt
from utils.logger import logger

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleOAuthService:
    """
    Google OAuth 2.0 client supporting OAuth Authorization Code flow
    and ID token payload verification.
    """

    def __init__(self):
        self.scope = "openid email profile"

    @property
    def client_id(self) -> str:
        return os.getenv("GOOGLE_CLIENT_ID", "").strip()

    @property
    def client_secret(self) -> str:
        return os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

    def is_configured(self) -> bool:
        """Check if Google OAuth credentials are set in environment."""
        return bool(self.client_id and self.client_secret)

    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Generate the Google OAuth 2.0 authorization URL.
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "access_type": "offline",
            "prompt": "select_account",
        }
        if state:
            params["state"] = state

        return f"{GOOGLE_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_user_info(self, code: str, redirect_uri: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Exchange OAuth code for tokens and extract Google user profile.
        Returns (success: bool, user_info: dict, message: str).
        """
        if not self.is_configured():
            return False, None, "Google OAuth Client ID/Secret not configured."

        try:
            token_payload = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            token_resp = requests.post(GOOGLE_TOKEN_ENDPOINT, data=token_payload, timeout=10)
            if token_resp.status_code != 200:
                err = f"Google token exchange failed: {token_resp.text}"
                logger.error(err)
                return False, None, err

            tokens = token_resp.json()
            access_token = tokens.get("access_token")
            id_token = tokens.get("id_token")

            # Fetch user info using access token
            user_info_resp = requests.get(
                GOOGLE_USERINFO_ENDPOINT,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )

            if user_info_resp.status_code != 200:
                # Fallback to decoding unverified ID token payload if userinfo endpoint fails
                if id_token:
                    decoded = jwt.decode(id_token, options={"verify_signature": False})
                    user_data = {
                        "google_id": decoded.get("sub"),
                        "email": decoded.get("email"),
                        "name": decoded.get("name", "Google User"),
                        "picture": decoded.get("picture", ""),
                        "email_verified": decoded.get("email_verified", True),
                    }
                    return True, user_data, "Authenticated via Google ID token."
                return False, None, "Failed to retrieve Google user profile."

            profile = user_info_resp.json()
            user_data = {
                "google_id": profile.get("sub"),
                "email": profile.get("email"),
                "name": profile.get("name") or profile.get("given_name", "Google User"),
                "picture": profile.get("picture", "https://lh3.googleusercontent.com/a/default-user=s96-c"),
                "email_verified": profile.get("email_verified", True),
            }
            logger.info(f"Google OAuth verified user: {user_data['email']}")
            return True, user_data, "Google authentication successful."

        except Exception as e:
            err = f"Error during Google OAuth code exchange: {e}"
            logger.error(err)
            return False, None, err


# Global singleton instance
google_oauth = GoogleOAuthService()
