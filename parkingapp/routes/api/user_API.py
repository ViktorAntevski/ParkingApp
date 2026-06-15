from flask import url_for, redirect, Blueprint, request, flash
from parkingapp.models.models import User, ActiveRegistrationPlate, HourlyParkingInvoice, EmailVerification, Resident
from flask_restful import Resource,Api, reqparse
from flask_login import login_user,logout_user,current_user,login_required
from zoneinfo import ZoneInfo
from parkingapp.auth.auth_decorators import user_required, verified_required
from parkingapp.services import user_services

Skopje_TZ = ZoneInfo("Europe/Skopje")

user_api_bp = Blueprint('user_api', __name__)
user_api = Api(user_api_bp)


start_hourly_metering = reqparse.RequestParser()
start_hourly_metering.add_argument("plates", type=str, required=True, help="insert your vehicle plates")
start_hourly_metering.add_argument("parking_zone", type=str, required=True, help="insert your parking zone")


#### Hourly parking

class StartHourlyParking(Resource):
    method_decorators = [login_required, user_required, verified_required]

    def post(self):

        args = start_hourly_metering.parse_args()

        return user_services.parking_start(args)

class FinalizeHourlyParking(Resource):

    def get(self):

        return user_services.parking_finalize()


stop_hourly_metering = reqparse.RequestParser()
stop_hourly_metering.add_argument("plates", required=True, location="json")

class StopHourlyParking(Resource):
    method_decorators = [login_required, user_required, verified_required]

    def post(self):

        args = stop_hourly_metering.parse_args()

        return user_services.stop_hourly_parking(args)

#######

add_resident = reqparse.RequestParser()
add_resident.add_argument("plates", type = str, required = True, help="Please provide your plates number", location="json")
add_resident.add_argument("zone", type = str, required = True, help="Please provide a valid parking zone. Check Price List for more info", location="json")

class RegisterResident(Resource):
    method_decorators = [login_required, user_required, verified_required]

    def post(self):

        args = add_resident.parse_args()

        return user_services.register_resident(args)


class MonthlySub(Resource):
    def post(self):
        pass



user_api.add_resource(StartHourlyParking, "/dashboard/api/hourly-parking-start")
user_api.add_resource(FinalizeHourlyParking, "/dashboard/api/hourly-parking-success")
user_api.add_resource(StopHourlyParking, "/dashboard/api/stop-hourly-parking")
user_api.add_resource(RegisterResident, "/dashboard/api/register-resident")