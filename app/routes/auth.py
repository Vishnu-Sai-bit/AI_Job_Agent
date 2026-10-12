"""
==========================================================
AI Job Copilot - Authentication Routes (Google OAuth, Gmail SMTP & JWT)
Author : Beere Vishnu Sai
==========================================================
"""

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
        redirect_uri = url_for("auth.google_callback", _external=True)
        # Ensure https in production
        if request.headers.get("X-Forwarded-Proto") == "https" and redirect_uri.startswith("http://"):
            redirect_uri = redirect_uri.replace("http://", "https://", 1)
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
            gmail_service.send_welcome_email(user.email, user.full_name)

        flash(f"Signed in with Google as {user.email}!", "success")
        return issue_jwt_response(url_for("main.dashboard"), user)

    return render_template("auth/google_select.html")


@auth_bp.route("/google/callback")
def google_callback():
    """
    Google OAuth 2.0 Callback handler:
    Exchanges code for tokens, verifies profile, issues JWT session.
    """
    code = request.args.get("code")
    if not code:
        err = request.args.get("error", "Access denied")
        flash(f"Google Sign-In was cancelled or failed ({err}).", "warning")
        return redirect(url_for("auth.login"))

    redirect_uri = url_for("auth.google_callback", _external=True)
    if request.headers.get("X-Forwarded-Proto") == "https" and redirect_uri.startswith("http://"):
        redirect_uri = redirect_uri.replace("http://", "https://", 1)

    success, profile, msg = google_oauth.exchange_code_for_user_info(code, redirect_uri)
    if not success or not profile:
        flash(f"Google OAuth verification failed: {msg}", "danger")
        return redirect(url_for("auth.login"))

    email = profile.get("email")
    name = profile.get("name", "Google Candidate")
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
        if picture and not user.avatar_url:
            user.avatar_url = picture
            db.session.commit()

    login_user(user)

    if is_new:
        gmail_service.send_welcome_email(user.email, user.full_name)

    flash(f"Signed in with Google as {user.email}!", "success")
    return issue_jwt_response(url_for("main.dashboard"), user)


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
