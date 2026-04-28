from flask_restful import Resource,Api, marshal_with, fields, reqparse, abort

api = Api(App)

add_sms_users = reqparse.RequestParser()
add_sms_Users.add_argument()
add_sms_Users.add_argument()
add_sms_Users.add_argument()


add_residents = reqparse.RequestParser()
add_residents.add_argument()
add_residents.add_argument()
add_residents.add_argument()


class SmsUsers(Resource):
    def post(self):


class Residents(Resource):

class MonthlySubs(Resource):


class Fined(Resource):
