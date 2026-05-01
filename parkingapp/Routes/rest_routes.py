from flask import Flask, url_for, redirect, Blueprint, request
from parkingapp.Models.models import User
from flask_restful import Resource,Api, marshal_with, fields, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user,logout_user,current_user
from parkingapp import db


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

#SignUp
add_user = reqparse.RequestParser()
add_user.add_argument("username", type = str, required = True, help="Provide a user name", location="json)
add_user.add_argument("password", type = str, required = True, help="Provide a password", location="json)
add_user.add_argument("name_surname", type=str, help="", required = True, location="json)
add_user.add_argument("address", type=str, help="", required = True, location="json)
add_user.add_argument("phone_number", type=str, help="", required = True, location="json)
add_user.add_argument("email_address", type=str, help="", required = True, location="json)
add_user.add_argument("ID_card", type=str, help="", required = True, location="json)

class UserSignUp(Resource):
    def post(self):
        args = add_user.parse_args()
        password = args["password"].strip()

        if User.query.filter_by(username=args['username']).first():
            return {'message': 'Username already taken'}, 400
        if User.query.filter_by(email_address=args['email_address']).first():
            return {'message': 'Email already taken'}, 400
        if len(password) < 8:
            return {'message': 'Passwords should be at least 8 characters long'}, 400
        user = User(
            username = args["username"].strip(), name_surname = args["name_surname"].strip(), address = args["address"].strip(),
            email_address = args["email_address"].strip().lower(), ID_card = args["ID_card"], phone_number =args["phone_number"]
        )
        user.set_password(args["password"])
        db.session.add(user)
        print("Reached commit")
        db.session.commit()
        return {"message": "User created successfully", "id": user.id}, 201

#LogIn
login_parser = reqparse.RequestParser()
login_parser.add_argument("username", type=str, required=True, help="Username required")
login_parser.add_argument("password", type=str, required=True, help="Password required")

class UserLogin(Resource):
    def post(self):
        args = login_parser.parse_args()

        user = User.query.filter_by(username=args["username"]).first()

        if not user or not user.check_password(args["password"]):
            return {"message": "Invalid username or password"}, 401

        login_user(user)

        return {
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username
        }, 200

        db.session.add(user)
        db.session.commit()


class ShortTermParkingResource(Resource):
    def post(self):
        pass



class MonthlySubs(Resource):
    def post(self):
        pass


class Fined(Resource):
    def post(self):
        pass


api.add_resource(UserSignUp, "/signup")
api.add_resource(UserLogin, "/login")
