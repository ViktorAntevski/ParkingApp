from flask import Flask, Blueprint, session
from flask_restful import Resource, Api
from auth import operator_required
from flask_login import login_required, login_user, logout_user,
from parkingapp import db
from Models.models import ActiveRegistrationPlate, Operator


operator_api_bp = Blueprint('api', __name__)
operator_api = Api(operator_api_bp)


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

class OperatorScan(Resource):
    @login_required
    @operator_required
    def get(self):
        vehicle_is_valid = db.session.execute(db.select(ActiveRegistrationPlate))










