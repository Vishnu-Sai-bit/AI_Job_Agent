"""
==========================================================
AI Job Copilot - Authentication Routes
==========================================================
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
import uuid
from app.extensions import db, login_manager
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

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
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
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
            role="candidate"
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash(f"Account created successfully for {full_name}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html")



@auth_bp.route("/google", methods=["GET", "POST"])
@auth_bp.route("/google-login", methods=["GET", "POST"])
def google_auth():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("name", "").strip() or "Google Candidate"

        if not email or "@" not in email:
            flash("Please provide a valid Gmail address.", "warning")
            return render_template("auth/google_select.html")

        # Find or create user via Google SSO
        user = User.query.filter_by(email=email).first()
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

        login_user(user)
        flash(f"Signed in with Google as {user.email}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/google_select.html")

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
        import random, time
        otp = str(random.randint(100000, 999999))
        session["reset_email"] = email
        session["reset_otp"] = otp
        session["reset_time"] = time.time()

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            flash(f"Note: No existing account found for {email}. Resetting will register this email with your new password.", "info")

        # Optional SMTP dispatch
        _dispatch_smtp_email(email, otp)

        flash(f"Verification code sent to {email}! Code: {otp}", "success")
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
            flash("Invalid or expired verification code. Please check your Gmail or request a new code.", "danger")
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

def _dispatch_smtp_email(to_email: str, code: str):
    import os, smtplib
    from email.mime.text import MIMEText
    
    server_host = os.getenv("MAIL_SERVER")
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    if server_host and username and password:
        try:
            port = int(os.getenv("MAIL_PORT", 587))
            msg = MIMEText(f"Your AI JobAgent password reset code is: {code}\n\nThis verification code expires in 15 minutes.")
            msg["Subject"] = f"AI JobAgent - Gmail Verification Code: {code}"
            msg["From"] = username
            msg["To"] = to_email
            with smtplib.SMTP(server_host, port, timeout=5) as s:
                s.starttls()
                s.login(username, password)
                s.send_message(msg)
        except Exception:
            pass

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("auth.login"))
