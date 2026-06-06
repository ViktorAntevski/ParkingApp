from flask import Flask, Blueprint, session
from flask_restful import Resource, Api, reqparse
from flask_login import login_required, login_user, logout_user
from parkingapp import db
from parkingapp.models.models import ActiveRegistrationPlate, Operator
from parkingapp.auth.auth_decorators import operator_required

operator_api_bp = Blueprint('operator_api', __name__)
operator_api = Api(operator_api_bp)


login_parser = reqparse.RequestParser()
login_parser.add_argument("username", type=str, required=True, help="Username required")
login_parser.add_argument("password", type=str, required=True, help="Password required")


class OperatorInspect(Resource):
    method_decorators = [login_required, operator_required]
    def get(self):
        vehicle_is_valid = db.session.execute(db.select(ActiveRegistrationPlate))


operator_api.add_resource(OperatorInspect, "/operator-inspect")






