from flask import request, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user
from flask_restful import Resource, Api, reqparse
from parkingapp.extensions import db
from parkingapp.models.models import User, EmailVerification, Operator
import secrets
from parkingapp.auth.email_verification import send_email
from datetime import datetime, timedelta

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
        password = args["password"].strip()
        username = args["username"].strip()
        email = args["email_address"].strip()

        if db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none():
            return {'message': 'Username already taken'
                    }, 400
        if db.session.execute(db.select(User).where(User.email_address == email)).scalar_one_or_none():
            return {'message': 'Email already taken'
                    }, 400
        if len(password) < 12 or len(password) > 30:
            return {'message': 'Passwords should be between 12 and 30 characters long'
                    }, 400
        if len(username) < 4 or len(username) > 30:
            return {'message': 'Username length should be between 4 and 30 characters long'
                    }, 400
        if "@" not in email:
            return {'message': 'Please enter a valid e-mail address'
                    }, 400
        user = User(
            username = args["username"].strip(), name_surname = args["name_surname"].strip(), address = args["address"].strip(),
            email_address = args["email_address"].strip().lower(), ID_card = args["ID_card"], phone_number =args["phone_number"]
        )
        user.set_password(args["password"])
        db.session.add(user)
        print("User added to db")
        db.session.commit()

        ##email verification###
        token = secrets.token_urlsafe(32)
        verification = EmailVerification(user_id=user.id, token=token, expires_at=datetime.utcnow()+timedelta(hours=24))
        db.session.add(verification)
        db.session.commit()
        send_email(user.email_address, token)

        return {"message": "A verification link has been sent to your e-mail", "user_id": user.id, "email":user.email_address
                }, 201


class VerifyEmail(Resource):
    def get(self):
        token_received = request.args.get("token")
        pending_user = db.session.execute(db.select(EmailVerification).where(EmailVerification.token == token_received)).scalar_one_or_none()
        if not token_received or not pending_user:
            return {"message":"Invalid token"
                    }, 400
        user = pending_user.user
        if not user:
            # should never happen (DB invariant)
            return {"message": "We couldn't verify your account. Please request a new verification email."
            }, 400

        if pending_user.expires_at < datetime.utcnow():
            return {"message":"Your token has expired"
                    }, 200
        user.is_verified = True
        db.session.delete(pending_user)
        db.session.commit()
        flash("Account is now verified, please log in again")
        return redirect("/login-page")


# LogIn
login_parser = reqparse.RequestParser()
login_parser.add_argument("username", type=str, required=True, help="Username required")
login_parser.add_argument("password", type=str, required=True, help="Password required")

class UserLogin(Resource):
    def post(self):
        args = login_parser.parse_args()
        password = args["password"].strip()
        username = args["username"].strip()
        user = db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none()

        if not user or not user.check_password(password):
            return {"message": "Invalid username or password"
                    }, 401
        login_user(user)

        if not user.is_verified:
            return {
                "message": "Account not verified",
                "redirect": url_for("pages.verify")
            }, 403

        return {
            "message": "Login successful",
        }, 200

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
        password = args["password"].strip()
        username = args["username"].strip()
        zone = args["zone"].strip()
        operator = db.session.execute(db.select(Operator).where(Operator.username == username)).scalar_one_or_none()

        if not operator or not operator.check_password(password):
            return {"message": "Invalid username or password"
                    }, 401
        login_user(operator)

        return {
            "message": "Login successful",
        }, 200

user_auth_api.add_resource(UserSignUp, "/signup")
user_auth_api.add_resource(VerifyEmail, "/verify-email")
user_auth_api.add_resource(UserLogin, "/login")
user_auth_api.add_resource(UserLogout, "/logout")
