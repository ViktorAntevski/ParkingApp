from flask import Blueprint
from flask_login import login_user
from flask_restful import reqparse, Resource, Api
from parkingapp.models.models import Operator
from parkingapp.extensions import db

operator_auth_api_bp = Blueprint('operator_auth', __name__)
operator_auth_api = Api(operator_auth_api_bp)

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

operator_auth_api.add_resource(OperatorLogin, "/operator-login")