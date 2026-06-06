from flask import url_for, redirect, Blueprint, request, flash
from parkingapp.models.models import User, ActiveRegistrationPlate, HourlyParkingInvoice, EmailVerification, Resident
from flask_restful import Resource,Api, reqparse
from flask_login import login_user,logout_user,current_user,login_required
from parkingapp import db
from pricing.price_list import ZONE_RATES
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import secrets
from flask_mail import Message
import re
from parkingapp.auth.auth_decorators import user_required, verified_required

Skopje_TZ = ZoneInfo("Europe/Skopje")
VALID_ZONES = {zone["zone"] for zone in ZONE_RATES}

user_api_bp = Blueprint('user_api', __name__)
user_api = Api(user_api_bp)

from parkingapp.extensions import mail
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


start_hourly_metering = reqparse.RequestParser()
start_hourly_metering.add_argument("plates", type=str, required=True, help="insert your vehicle plates")
start_hourly_metering.add_argument("parking_zone", type=str, required=True, help="insert your parking zone")

class HourlyParking(Resource):
    method_decorators = [login_required, user_required, verified_required]

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
    method_decorators = [login_required, user_required, verified_required]

    def post(self):
        user_id = current_user.id
        args = stop_hourly_metering.parse_args()
        plates = args["plates"]

        active = db.session.execute(db.select(ActiveRegistrationPlate).where(
            ActiveRegistrationPlate.vehicle_reg_plate == plates
        )).scalar_one_or_none()

        invoice = active.hourly_invoice

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
    method_decorators = [login_required, user_required, verified_required]

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


user_api.add_resource(HourlyParking, "/hourly-parking")
user_api.add_resource(StopHourlyParking, "/stop-hourly-parking")
user_api.add_resource(RegisterResident, "/api-register-resident")