from flask import Flask, url_for, redirect, Blueprint, request, flash
from parkingapp.Models.models import User, ActiveRegistrationPlate, HourlyParkingInvoice, EmailVerification, Resident
from flask_restful import Resource,Api, marshal_with, fields, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user,logout_user,current_user,login_required, LoginManager
from parkingapp import db
from parkingapp.price_list import ZONE_RATES
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import tzdata
import secrets
from flask_mail import Message
from parkingapp.extensions import mail
import re
from functools import wraps

Skopje_TZ = ZoneInfo("Europe/Skopje")
VALID_ZONES = {zone["zone"] for zone in ZONE_RATES}

api_bp = Blueprint('api', __name__)
api = Api(api_bp)



def verified_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("pages.login_page"))

        if not current_user.is_verified:
            return redirect(url_for("pages.verify"))

        return f(*args, **kwargs)
    return wrapper



def send_email(to_email, token):
    verification_link = f"http://localhost:5000/verify-email?token={token}"

    msg = Message(
        subject="Verify your email",
        sender = "vantevski1@gmail.com",
        recipients=[to_email]
    )

    msg.body = f"""
Hi,

Please click the link below to verify your account:

{verification_link}

If you did not sign up, you can ignore this email.

Best regards,
ParkingApp Team
"""

    mail.send(msg)

def valid_parking_zone(zone):
    if zone not in VALID_ZONES:
        return {"message": "Incorrect parking zone"
                }, 400


def valid_plates(plates):
    pattern = r'^[A-Za-z]{2}[0-9]{4}[A-Za-z]{2}$'
    if not re.match(pattern, plates):
        return {
        "message": "Insert valid plates"
    }, 400

def duplicate_plates(plates):
    plates_written_in_sys = db.session.execute(
        db.select(ActiveRegistrationPlate).where(ActiveRegistrationPlate.vehicle_reg_plate == plates)).scalar_one_or_none()
    if plates_written_in_sys:
        return {
            "message": "This vehicle is already registered in our system"
        }, 400




#SignUp
add_user = reqparse.RequestParser()
add_user.add_argument("username", type = str, required = True, help="Provide a user name", location="json")
add_user.add_argument("password", type = str, required = True, help="Provide a password", location="json")
add_user.add_argument("name_surname", type=str, help="", required = True, location="json")
add_user.add_argument("address", type=str, help="", required = True, location="json")
add_user.add_argument("phone_number", type=str, help="", required = True, location="json")
add_user.add_argument("email_address", type=str, help="", required = True, location="json")
add_user.add_argument("ID_card", type=str, help="", required = True, location="json")



#######################ROUTES#########################################

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
        user = db.session.execute(db.select(User).where(User.id == pending_user.user_id)).scalar_one_or_none()
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
            "user_id": user.id,
            "username": user.username,
            "is_verified":user.is_verified
        }, 200

class UserLogout(Resource):
    def post(self):
        logout_user()

        return {
            "message": "Logged out successfully"
        }, 200

start_hourly_metering = reqparse.RequestParser()
start_hourly_metering.add_argument("plates", type=str, required=True, help="insert your vehicle plates")
start_hourly_metering.add_argument("parking_zone", type=str, required=True, help="insert your parking zone")

class HourlyParking(Resource):
    method_decorators = [login_required, verified_required]

    def post(self):

        user_id = current_user.id
        args = start_hourly_metering.parse_args()
        zone = args["parking_zone"]
        plates = args["plates"]

        error = valid_parking_zone(zone)
        if error:
            return error

        error = valid_plates(plates)
        if error:
            return error

        error = duplicate_plates(plates)
        if error:
            return error

        parking = ActiveRegistrationPlate(user_id=user_id, vehicle_reg_plate=plates,registered_parking_zone=zone)
        invoice = HourlyParkingInvoice(user_id=user_id, vehicle_reg_plate=plates)


        db.session.add(parking)
        db.session.add(invoice)
        print("commited reached")
        db.session.commit()

        return {
            "message": "Hourly parking started successfully"
        }, 201


stop_hourly_metering = reqparse.RequestParser()
stop_hourly_metering.add_argument(
    "plates", required=True, location="json")

class StopHourlyParking(Resource):
    method_decorators = [login_required, verified_required]

    def post(self):
        user_id = current_user.id
        args = stop_hourly_metering.parse_args()
        plates = args["plates"]

        active = db.session.execute(db.select(ActiveRegistrationPlate).where(
            ActiveRegistrationPlate.vehicle_reg_plate == plates
        )).scalar_one_or_none()

        invoice = db.session.execute(db.select(HourlyParkingInvoice).where(
            HourlyParkingInvoice.vehicle_reg_plate  == plates)).scalar_one_or_none()

        if not invoice or not active:
            return {
                "message": "No active invoice found"
            }, 500

        now = datetime.now(Skopje_TZ)
        check_in = invoice.check_in.replace(tzinfo=Skopje_TZ)
        duration = now - check_in

        total_hours = int(duration.total_seconds() // 3600)

        zone = active.registered_parking_zone
        h_rate = None

        for r in ZONE_RATES:
            if r["zone"] == zone:
                h_rate = r["h_rate"]
                break

        if h_rate is None:
            return {"message": "Invalid parking zone for billing"
                    }, 500

        if total_hours == 0:
            total_hours = 1
        total_invoice = (h_rate) * total_hours

        try:
            db.session.delete(active)
            db.session.delete(invoice)
            print(total_hours,total_invoice)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"message": "Failed to stop parking"
                    }, 500

        return {
        "message": f"Parking stopped successfully, The total cost of the parking service is {total_invoice} denars"
    }, 201

add_resident = reqparse.RequestParser()
add_resident.add_argument("plates", type = str, required = True, help="Please provide your plates number", location="json")
add_resident.add_argument("zone", type = str, required = True, help="Please provide a valid parking zone. Check Price List for more info", location="json")

class RegisterResident(Resource):
    method_decorators = [login_required]

    def post(self):
        print(current_user.id)
        user_id = current_user.id
        args = add_resident.parse_args()
        plates = args["plates"]
        zone = args["zone"]

        error = valid_parking_zone(zone)
        if error:
            return error

        error = valid_plates(plates)
        if error:
            return error

        error = duplicate_plates(plates)
        if error:
            return error

        plates_written_in_sys = ActiveRegistrationPlate(vehicle_reg_plate=plates, user_id=user_id, registered_parking_zone=zone)
        resident = Resident(vehicle_reg_plate=plates, user_id=user_id)
        db.session.add(plates_written_in_sys)
        db.session.add(resident)
        db.session.commit()
        return {"message": "Your vehicle registration is pending. Please go to your nearest ParkingApp office and confirm your identity"
                }, 201


class MonthlySub(Resource):
    def post(self):
        pass


class Fined(Resource):
    def post(self):
        pass


api.add_resource(UserSignUp, "/signup")
api.add_resource(VerifyEmail, "/verify-email")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(HourlyParking, "/hourly-parking")
api.add_resource(StopHourlyParking, "/stop-hourly-parking")
api.add_resource(RegisterResident, "/api-register-resident")