from flask import request, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user
from flask_restful import Resource, Api, reqparse
from parkingapp.extensions import db
from parkingapp.models.models import User, EmailVerification, Operator
import secrets
from parkingapp.auth.email_verification import send_email
from datetime import datetime, timedelta
from parkingapp.services import auth_services

user_auth_api_bp = Blueprint('user_auth', __name__)
user_auth_api = Api(user_auth_api_bp)


#SignUp
add_user = reqparse.RequestParser()
add_user.add_argument("username", type = str, required = True, help="Provide a user name", location="json")
add_user.add_argument("password", type = str, required = True, help="Provide a password", location="json")
add_user.add_argument("name_surname", type=str, help="", required = True, location="json")
add_user.add_argument("address", type=str, help="", required = True, location="json")
add_user.add_argument("phone_number", type=str, help="", required = True, location="json")
add_user.add_argument("email_address", type=str, help="", required = True, location="json")
add_user.add_argument("ID_card", type=str, help="", required = True, location="json")

class UserSignUp(Resource):
    def post(self):

        args = add_user.parse_args()

        return auth_services.create_user(args)

class VerifyEmail(Resource):
    def get(self):

        token_received = request.args.get("token")

        return auth_services.verify_email(token_received)

class VerificationResend(Resource):
    def post(self):

        email = request.json.get("email")

        return auth_services.resend(email)
# LogIn
login_parser = reqparse.RequestParser()
login_parser.add_argument("username", type=str, required=True, help="Username required")
login_parser.add_argument("password", type=str, required=True, help="Password required")

class UserLogin(Resource):
    def post(self):

        args = login_parser.parse_args()

        return auth_services.user_login(args)

class UserLogout(Resource):
    def post(self):
        logout_user()

        return {
            "message": "Logged out successfully"
        }, 200

login_parser = reqparse.RequestParser()
login_parser.add_argument("username", type=str, required=True, help="Username required")
login_parser.add_argument("password", type=str, required=True, help="Password required")

class OperatorLogin(Resource):
    def post(self):

        args = login_parser.parse_args()

        return auth_services.operator_login(args)

user_auth_api.add_resource(UserSignUp, "/signup")
user_auth_api.add_resource(VerifyEmail, "/verify-email")
user_auth_api.add_resource(UserLogin, "/login")
user_auth_api.add_resource(UserLogout, "/logout")
user_auth_api.add_resource(VerificationResend, "/verification-resend")