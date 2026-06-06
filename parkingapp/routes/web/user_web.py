from flask import Blueprint, render_template
from flask_login import login_required, current_user
from pricing.price_list import ZONE_RATES
from routes.api.user_API import verified_required
from parkingapp.auth.user_loader import user_required

dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")
@dashboard.before_request
@login_required
@user_required
@verified_required
def enforce_auth():
    pass


@dashboard.route("")
def dashboard_menu():
    return render_template("dashboard.html", user=current_user)


@dashboard.route("/hourly-parking")
def hourly_parking():
    return render_template("dashboard_hourlyparking.html", user=current_user)

@dashboard.route("/subscribe-monthly")
def subscribe_monthly():
    return render_template("dashboard_subsmonthly.html", user=current_user)

@dashboard.route("/register-for-residents")
def reg_for_res():
    return render_template("dashboard_register_residents.html", user=current_user)

@dashboard.route("/service-price-list")
def price_list():
    return render_template("dashboard_pricelist.html", user=current_user, prices=ZONE_RATES)

@dashboard.route("/stop-parking")
def stop_parking():
    return render_template("dashboard_stopparking.html", user=current_user)