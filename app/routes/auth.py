"""
==========================================================
AI Job Copilot - Authentication Routes
==========================================================
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
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

@auth_bp.route("/guest", methods=["GET", "POST"])
@auth_bp.route("/guest-login", methods=["GET", "POST"])
def guest_login():
    guest_user = User.query.filter_by(email="guest@jobcopilot.ai").first()
    if not guest_user:
        guest_user = User(
            id="usr_guest_demo",
            email="guest@jobcopilot.ai",
            full_name="Guest Candidate",
            role="candidate"
        )
        guest_user.set_password("guest123")
        db.session.add(guest_user)
        db.session.commit()

    login_user(guest_user)
    flash("Signed in with Guest Candidate access!", "info")
    return redirect(url_for("main.dashboard"))

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("auth.login"))
