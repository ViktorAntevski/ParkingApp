from flask import Flask
from flask_restful import Resource

from Models.models import ActiveRegistrationPlate

class OperatorLogin(Resource):

    def post(self):

class OperatorScan(Resource):

    def get(self):
        vehicle_is_valid = db.session.execute(db.select(ActiveRegistrationPlate))










