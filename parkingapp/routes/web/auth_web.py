from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import current_user
from parkingapp.models.models import EmailVerification, User
from parkingapp import db
from parkingapp.auth.email_verification import send_email
import secrets
from datetime import datetime, timedelta

pages = Blueprint("pages", __name__)


@pages.route("/")
def home():
    return render_template("homepage.html")


@pages.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")


@pages.route("/login-page", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        if current_user.is_verified:
            return redirect(url_for("dashboard.dashboard_menu"))
        return redirect(url_for("pages.verify"))
    return render_template("login.html")


@pages.route("/operator-login-page", methods=["GET"])
def operator_login_page():
    if current_user.is_authenticated:
        return redirect(url_for("operator_dashboard.dashboard_menu"))
    return render_template("operator_login.html")


@pages.route("/verification-required", methods=["GET"])
def verify():
    return render_template("verify.html")


@pages.route("/verify-email1", methods=["GET"])
def verify_email():
    token=request.args.get("token")

    if not token:
        return {"message":"Missing token"}

    token_record = EmailVerification.query.filter_by(token=token).first()
    if not token_record:
        return {"message":"Invalid token"}
    if token_record.expires_at < datetime.now():
        return {"message":"Token expired"}
    user = User.query.get(token_record.user_id)
    if not user:
        return {"message": "We couldn't verify your account. Please request a new verification email."}
    user.is_verified = True

    db.session.delete(token_record)
    db.session.commit()

    return  redirect("/dashboard?verified=true")


@pages.route("/operator-login-page")
def operator_login():
    return render_template("operator_dashboard.html")