"""
==========================================================
AI Job Copilot - Authentication Routes (Google OAuth, Gmail SMTP & JWT)
Author : Beere Vishnu Sai
==========================================================
"""

import os
import uuid
import time
import random
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, make_response
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db, login_manager
from app.models.user import User
from services.email.gmail_smtp import gmail_service
from services.auth.google_oauth import google_oauth
from services.auth.auth_service import AuthService
from utils.logger import logger

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def issue_jwt_response(redirect_target, user):
    """
    Generate signed JWT token, store in session, and set secure HTTP cookie.
    """
    token = AuthService.generate_token(
        user_id=user.id,
        email=user.email,
        name=user.full_name,
        role=getattr(user, "role", "candidate"),
        auth_provider=getattr(user, "auth_provider", "local")
    )
    session["jwt_token"] = token
    resp = make_response(redirect(redirect_target))
    resp.set_cookie("jwt_token", token, max_age=7 * 24 * 3600, httponly=True, samesite="Lax")
    return resp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            return issue_jwt_response(url_for("main.dashboard"), user)
        else:
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password or not full_name:
            flash("All fields are required.", "warning")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email address already registered.", "warning")
            return render_template("auth/register.html")

        new_user = User(
            id=f"usr_{uuid.uuid4().hex[:12]}",
            email=email,
            full_name=full_name,
            role="candidate",
            auth_provider="local"
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        # Dispatch welcome email via Gmail SMTP
        gmail_service.send_welcome_email(email, full_name)

        flash(f"Account created successfully for {full_name}!", "success")
        return issue_jwt_response(url_for("main.dashboard"), new_user)

    return render_template("auth/register.html")


def _build_google_callback_uri() -> str:
    """
    Build canonical callback URI matching Google Cloud Console configuration.
    Handles Render reverse proxy (HTTPS) vs local development automatically.
    """
    override = os.getenv("GOOGLE_REDIRECT_URI")
    if override:
        return override.strip()

    is_production = (
        "onrender.com" in request.host
        or request.headers.get("X-Forwarded-Proto") == "https"
        or request.is_secure
    )

    scheme = "https" if is_production else "http"
    callback_url = url_for("auth.google_callback", _external=True, _scheme=scheme)

    if is_production and callback_url.startswith("http://"):
        callback_url = callback_url.replace("http://", "https://", 1)

    return callback_url


@auth_bp.route("/google", methods=["GET", "POST"])
@auth_bp.route("/google-login", methods=["GET", "POST"])
def google_auth():
    """
    Google OAuth 2.0 Entrypoint:
    - If GOOGLE_CLIENT_ID & SECRET are configured, redirects to real Google Accounts authorization.
    - Otherwise, provides interactive Google account selector for seamless development.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    # Check if real Google OAuth 2.0 credentials are configured
    if google_oauth.is_configured() and request.method == "GET":
        redirect_uri = _build_google_callback_uri()
        return redirect(google_oauth.get_authorization_url(redirect_uri))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("name", "").strip() or "Google Candidate"

        if not email or "@" not in email:
            flash("Please provide a valid Gmail address.", "warning")
            return render_template("auth/google_select.html")

        # Find or create user via Google SSO
        user = User.query.filter_by(email=email).first()
        is_new = False
        if not user:
            user = User(
                id=f"usr_{uuid.uuid4().hex[:12]}",
                email=email,
                full_name=full_name,
                role="candidate",
                auth_provider="google",
                avatar_url="https://lh3.googleusercontent.com/a/default-user=s96-c"
            )
            db.session.add(user)
            db.session.commit()
            is_new = True

        login_user(user)

        if is_new:
            try:
                gmail_service.send_welcome_email(user.email, user.full_name)
            except Exception as mail_err:
                logger.warning(f"Welcome email notice: {mail_err}")

        flash(f"Signed in with Google as {user.email}!", "success")
        return issue_jwt_response(url_for("main.dashboard"), user)

    return render_template("auth/google_select.html")


@auth_bp.route("/google/callback")
def google_callback():
    """
    Google OAuth 2.0 Callback handler:
    Exchanges code for tokens, verifies profile, issues JWT session.
    Guaranteed zero unhandled exceptions (catches all failure cases and redirects cleanly).
    """
    try:
        code = request.args.get("code")
        if not code:
            err = request.args.get("error", "Access denied or cancelled by user")
            flash(f"Google Sign-In was cancelled or failed ({err}).", "warning")
            return redirect(url_for("auth.login"))

        redirect_uri = _build_google_callback_uri()

        success, profile, msg = google_oauth.exchange_code_for_user_info(code, redirect_uri)
        if not success or not profile:
            logger.warning(f"Google OAuth token exchange failed: {msg}")
            flash(f"Google OAuth verification failed: {msg}", "danger")
            return redirect(url_for("auth.login"))

        email = profile.get("email")
        if not email:
            flash("Google account did not provide a valid email address.", "danger")
            return redirect(url_for("auth.login"))

        name = profile.get("name") or profile.get("given_name") or email.split("@")[0].title()
        picture = profile.get("picture", "https://lh3.googleusercontent.com/a/default-user=s96-c")
        google_id = profile.get("google_id", "")

        user = User.query.filter_by(email=email).first()
        is_new = False
        if not user:
            user = User(
                id=f"usr_{uuid.uuid4().hex[:12]}",
                email=email,
                full_name=name,
                role="candidate",
                auth_provider="google",
                google_id=google_id,
                avatar_url=picture
            )
            db.session.add(user)
            db.session.commit()
            is_new = True
        else:
            updated = False
            if picture and not getattr(user, "avatar_url", None):
                user.avatar_url = picture
                updated = True
            if google_id and not getattr(user, "google_id", None):
                user.google_id = google_id
                updated = True
            if getattr(user, "auth_provider", None) != "google":
                user.auth_provider = "google"
                updated = True
            if updated:
                db.session.commit()

        login_user(user)

        if is_new:
            try:
                gmail_service.send_welcome_email(user.email, user.full_name)
            except Exception as mail_err:
                logger.warning(f"Welcome email delivery warning via Gmail SMTP: {mail_err}")

        flash(f"Signed in with Google as {user.email}!", "success")
        return issue_jwt_response(url_for("main.dashboard"), user)

    except Exception as exc:
        logger.exception(f"Unhandled exception during Google OAuth callback: {exc}")
        flash(f"Google Sign-In encountered an issue: {exc}. Please try again or sign in with password.", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email or "@" not in email:
            flash("Please enter a valid Gmail / Email address.", "warning")
            return render_template("auth/forgot_password.html")

        # Generate secure 6-digit verification code
        otp = str(random.randint(100000, 999999))
        session["reset_email"] = email
        session["reset_otp"] = otp
        session["reset_time"] = time.time()

        user = User.query.filter_by(email=email).first()
        user_name = user.full_name if user else "Candidate"

        # Dispatch real email via Google SMTP (Gmail)
        sent, status_msg = gmail_service.send_password_reset_otp(email, otp, user_name)

        if sent:
            flash(f"A 6-digit verification code has been dispatched to your Gmail inbox ({email})!", "success")
        else:
            flash(
                f"Verification code generated: {otp} (Gmail SMTP status: {status_msg})",
                "info"
            )

        return redirect(url_for("auth.reset_password", email=email))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    target_email = request.args.get("email") or session.get("reset_email", "")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        code = request.form.get("code", "").strip()
        new_password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        stored_otp = session.get("reset_otp")
        stored_email = session.get("reset_email")

        # Verify OTP code
        if not code or code != stored_otp or email != stored_email:
            flash("Invalid or expired verification code. Please request a new code.", "danger")
            return render_template("auth/reset_password.html", email=email)

        if not new_password or len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return render_template("auth/reset_password.html", email=email)

        if new_password != confirm_password:
            flash("Passwords do not match.", "warning")
            return render_template("auth/reset_password.html", email=email)

        # Update or create user account
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
        else:
            name_guess = email.split("@")[0].replace(".", " ").title()
            user = User(
                id=f"usr_{uuid.uuid4().hex[:12]}",
                email=email,
                full_name=name_guess,
                role="candidate",
                auth_provider="local"
            )
            user.set_password(new_password)
            db.session.add(user)
            db.session.commit()

        # Clear reset session
        session.pop("reset_otp", None)
        session.pop("reset_email", None)
        session.pop("reset_time", None)

        flash("Password successfully reset! You can now sign in with your new password.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", email=target_email)


@auth_bp.route("/me", methods=["GET"])
def me():
    """
    JWT Verification Endpoint:
    Returns the decoded JWT payload and identity status for client applications.
    """
    token = AuthService.get_token_from_request(request)
    if not token:
        return jsonify({"authenticated": False, "error": "No JWT token provided"}), 401

    payload = AuthService.verify_token(token)
    if not payload:
        return jsonify({"authenticated": False, "error": "Invalid or expired JWT token"}), 401

    return jsonify({
        "authenticated": True,
        "user": {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "role": payload.get("role"),
            "auth_provider": payload.get("auth_provider"),
        },
        "jwt_token": token
    })


@auth_bp.route("/logout")
@login_required
def logout():
    session.pop("jwt_token", None)
    logout_user()
    flash("You have been signed out successfully.", "info")
    resp = make_response(redirect(url_for("auth.login")))
    resp.delete_cookie("jwt_token")
    return resp
