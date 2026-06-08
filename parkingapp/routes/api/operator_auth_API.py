from flask import Blueprint
from flask_login import logout_user
from flask_restful import reqparse, Resource, Api
from parkingapp.services import auth_services

operator_auth_api_bp = Blueprint('operator_auth', __name__)
operator_auth_api = Api(operator_auth_api_bp)

login_parser = reqparse.RequestParser()
login_parser.add_argument("username", type=str, required=True, help="Username required")
login_parser.add_argument("password", type=str, required=True, help="Password required")
login_parser.add_argument("zone", type=str, required=True, help="Working zone required")

class OperatorLogin(Resource):
    def post(self):

        args = login_parser.parse_args()

        return auth_services.operator_login(args)

class OperatorLogout(Resource):
    def post(self):
        logout_user()

        return {
            "message": "Logged out successfully"
        }, 200

operator_auth_api.add_resource(OperatorLogin, "/operator-login")
operator_auth_api.add_resource(OperatorLogout, "/operator-logout")