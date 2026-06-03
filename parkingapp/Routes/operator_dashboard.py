from flask import Blueprint, render_template, url_for, request, redirect , abort
from flask_login import login_required, current_user
from parkingapp.auth import operator_required



operator_dashboard = Blueprint("/operator", __name__, url_prefix="/operator")
@operator_dashboard.before_request
@login_required
@operator_required

@operator_dashboard.route("")
def operator_dashboard_menu():
    return render_template("operator_dashboard.html", user=current_user)

@operator_dashboard.route("")
def inspect():
    return render_template("inspect.html", user=current_user)