from parkingapp.parkingapp import db
from flask_sqlalchemy import SQLAlchemy

#base class: RegistrationPlates, operator queries here
class RegistrationPlates(db.Model):
    __tablename__ = "current_users"
    id = db.Column(db.Integer, primary_key=True)
    vehicle_reg_plate = db.Column(db.String(20), unique=True, nullable=False)
    phone_number = db.Column(db.String(20),unique=True, nullable=False)
    registered_parking_zone = db.Column(db.String(5), nullable=False)
    fined = db.Column(db.Boolean, default=False)

#subtype tables
class SmsUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, foreign_key="current_users.id")
    check_in = db.Column(db.Datetime(timezone=True), default=lambda: datetime.now(Skopje_TZ), nullable=False)

class MonthlySubs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, foreign_key="current_users.id")
    address = db.Column(db.String(100), nullable=False)
    name_surname = db.Column(db.String(50), nullable=False)
    ID_card = db.Column(db.String(20), nullable=False)
    payed_for_month = db.Column(db.Boolean, default = False)

class Residents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, foreign_key="current_users.id")
    address = db.Column(db.String(100), nullable=False)
    name_surname = db.Column(db.String(50), nullable=False)
    ID_card = db.Column(db.String(20), nullable=False)

class Guests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, foreign_key="current_users.id")


#class GuestCards(db.Model):