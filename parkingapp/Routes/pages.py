from flask import Blueprint, render_template, url_for, request, redirect , abort
from flask_login import login_required, current_user
from parkingapp.price_list import ZONE_RATES
from datetime import datetime
from parkingapp.Models.models import EmailVerification, User
from parkingapp import db
from parkingapp.Routes.user_routes import send_email
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
            return redirect(url_for("/dashboard.dashboard_menu"))
        return redirect(url_for("pages.verify"))
    return render_template("login.html")

@pages.route("/operator-login-page", methods=["GET"])
def operator_login_page():
    if current_user.is_authenticated:
        return redirect(url_for("/dashboard.dashboard_menu"))
    return render_template("login.html")

@pages.route("/verification-required", methods=["GET"])
def verify():
    return render_template("verify.html")

@pages.route( "/verification-resend",methods=["POST"])
def resend():
    email = request.json.get("email")
    if not email or "@" not in email:
        return {"message": "Please enter a valid e-mail"}, 400
    token = secrets.token_urlsafe(32)
    user = User.query.filter_by(email_address=email).first()
    if not user:
        return {"message": "The e-mail you entered is not the e-mail you submitted during sign-up"}, 400

    now = datetime.utcnow()
    if user.last_resend and now - user.last_resend < timedelta(seconds=60):
        return {"message": "Try again in 1 minute"}
    user.last_resend = now
    verification = EmailVerification(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.session.add(verification)
    db.session.commit()
    send_email(email, token)

    return {"message": "Verification email sent"}, 200


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