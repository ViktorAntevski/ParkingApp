from flask import Flask, url_for, redirect
from flask_restful import Resource,Api, marshal_with, fields, reqparse, abort


api = Api(App)

add_shortterm_users = reqparse.RequestParser()
add_shortterm_Users.add_argument("phone_number", type=str, help="")
add_shortterm_Users.add_argument()
add_shortterm_Users.add_argument()


add_residents = reqparse.RequestParser()
add_residents.add_argument()
add_residents.add_argument()
add_residents.add_argument()


class ShortTermParking(Resource):
    def post(self):


class Residents(Resource):

class MonthlySubs(Resource):


class Fined(Resource):


api.add_resource(SmsUsers, )