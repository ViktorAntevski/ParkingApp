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
    if current_user.is_authenticated:
        return redirect(url_for("pages.dashboard"))
    return render_template("login.html")

@pages.route("/verification-required", methods=["GET"])
def verify():
    return render_template("verify.html")

@pages.route( "/verification-resend",methods=["POST"])
def resend():
    email = request.json.get("email")
    token = secrets.token_urlsafe(32)

    verification = EmailVerification(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )

    db.session.add(verification)
    db.session.commit()

    send_email(user.email_address, token)

    return {"message": "Verification email sent"}, 200


return


@pages.route("/verify-email", methods=["GET"])
def verify_email():
    token=request.args.get("token")

    if not token:
        return {"message":"Missing token"}

    token_record = EmailVerification.query.filter_by(token=token).first()
    if not token_record:
        return {"message":"Invalid token"}
    if token_record.expires_at < datetime.now:
        return {"message":"Token expired"}
    user = User.query.get(token_record.user_id).first()
    user.is_verified = True

    db.session.delete(token_record)
    db.session.commit()

    return {"message": "Email verified successfully!"}


    return render_template("verify.html")

@pages.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@pages.route("/dashboard/hourly-parking")
@login_required
def hourly_parking():
    return render_template("dashboard_hourlyparking.html", user=current_user)

@pages.route("/dashboard/subscribe-monthly")
@login_required
def subscribe_monthly():
    return render_template("dashboard_subsmonthly.html", user=current_user)

@pages.route("/dashboard/register-for-residents")
@login_required
def reg_for_res():
    return render_template("dashboard_register_residents.html", user=current_user)

@pages.route("/dashboard/service-price-list")
@login_required
def price_list():
    return render_template("dashboard_pricelist.html", user=current_user, prices=ZONE_RATES,)

@pages.route("/dashboard/stop-parking")
@login_required
def stop_parking():
    return render_template("dashboard_stopparking.html", user=current_user)

@pages.route("/operators")
def operator_login():
    return render_template("operator_dashboard.html")