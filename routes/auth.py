from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from models import db
from models.user import User, PasswordResetToken
from utils.audit import log_action

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form["email"]).first():
            flash("Email already exists.", "warning")
            return redirect(url_for("auth.register"))
        user = User(full_name=request.form["full_name"], email=request.form["email"], role="User")
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()
        log_action(user.email, "REGISTER")
        flash("Registration complete.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            log_action(user.email, "LOGIN")
            return redirect(url_for("dashboard.home"))
        log_action(request.form.get("email", "unknown"), "LOGIN", status="failed")
        flash("Invalid credentials", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    reset_token = None
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user:
            reset_token = PasswordResetToken.issue_for_user(user.id).token
            log_action(user.email, "FORGOT_PASSWORD")
        flash("If the account exists, a reset token has been generated for demo purposes.", "info")
    return render_template("auth/forgot_password.html", reset_token=reset_token)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    token_row = PasswordResetToken.query.filter_by(token=token, used=False).first()
    if not token_row or token_row.expires_at < datetime.utcnow():
        flash("Token is invalid or expired.", "danger")
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        user = User.query.get(token_row.user_id)
        user.set_password(request.form["password"])
        token_row.used = True
        db.session.commit()
        log_action(user.email, "RESET_PASSWORD")
        flash("Password updated. Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html")


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        log_action(current_user.email, "LOGOUT")
        logout_user()
    return redirect(url_for("auth.login"))
