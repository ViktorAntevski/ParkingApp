from flask import Blueprint, render_template, url_for, request, redirect , abort
from flask_login import login_required, current_user
from parkingapp.price_list import ZONE_RATES
from datetime import datetime
from parkingapp.Models.models import EmailVerification, User
from parkingapp import db
from parkingapp.Routes.rest_routes import send_email
import secrets
from datetime import datetime, timedelta

pages = Blueprint("pages", __name__)

@pages.route("/")
def home():
    return render_template("homepage.html")

@pages.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")

@pages.route("/login", methods=["GET"])
def login_page():
    print(current_user)
    if current_user.is_authenticated:
        if current_user.is_verified:
            return redirect(url_for("dashboard.dashboard_menu"))
        return redirect(url_for("pages.verify"))
    return render_template("login.html")

@pages.route("/verification-required", methods=["GET"])
def verify():
    return render_template("verify.html")

@pages.route( "/verification-resend",methods=["POST"])
def resend():
    user_id = request.json.get("user")
    token = secrets.token_urlsafe(32)
    print("user")

    user = User.query.filter_by(id=user_id).first()
    email = user.email_address

    verification = EmailVerification(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.session.add(verification)
    db.session.commit()

    send_email(email, token)

    return {"message": "Verification email sent"}, 200


@pages.route("/verify-email", methods=["GET"])
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
    user.is_verified = True

    db.session.delete(token_record)
    db.session.commit()

    return  redirect("/dashboard?verified=true")


    return render_template("verify.html")

@pages.route("/operators")
def operator_login():
    return render_template("operator_dashboard.html")