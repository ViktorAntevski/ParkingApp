from flask import Flask, Blueprint, session
from flask_restful import Resource, Api, reqparse
from flask_login import login_required, login_user, logout_user
from parkingapp.auth.auth_decorators import operator_required
from parkingapp.services import operator_services

operator_api_bp = Blueprint('operator_api', __name__)
operator_api = Api(operator_api_bp)


inspect_plate_parser = reqparse.RequestParser()
inspect_plate_parser.add_argument("plate", type=str, required=True, help="Reg Plate required")

class PlateCheck(Resource):
    method_decorators = [login_required, operator_required]
    def post(self):

        args = inspect_plate_parser.parse_args()

        return operator_services.plate_check(args)


change_zone_parser = reqparse.RequestParser()
change_zone_parser.add_argument("zone", type=str, required=True, help="Username required")

class ChangeZone(Resource):
    method_decorators = [login_required, operator_required]
    def post(self):

        args = change_zone_parser.parse_args()

        return operator_services.change_zone(args)


operator_api.add_resource(PlateCheck, "/operator/plate-check")
operator_api.add_resource(ChangeZone, "/operator/change-zone")





