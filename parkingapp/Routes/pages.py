from flask import Blueprint, render_template, url_for, request, redirect , abort
from flask_login import login_required, current_user


pages = Blueprint("pages", __name__)

@pages.route("/")
def home():
    return render_template("homepage.html")

@pages.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")

@pages.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@pages.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)
