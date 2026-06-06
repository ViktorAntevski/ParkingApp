from flask import Blueprint, render_template, url_for, request, redirect , abort
from flask_login import login_required, current_user
from parkingapp.auth.auth_decorators import operator_required



operator_dashboard = Blueprint("operator_dashboard", __name__, url_prefix="/operator")
@operator_dashboard.before_request
@login_required
@operator_required
def enforce_auth():
     pass

@operator_dashboard.route("")
def dashboard_menu():
    return render_template("operator_dashboard.html", user=current_user)

@operator_dashboard.route("")
def inspect():
    return render_template("inspect.html", user=current_user)