from parkingapp import db
from flask_login import UserMixin
from datetime import datetime
from zoneinfo import ZoneInfo
from parkingapp import bcrypt
import tzdata

Skopje_TZ = ZoneInfo("Europe/Skopje")


class User(db.Model, UserMixin):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    name_surname = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    email_address = db.Column(db.String(50), unique=True, nullable=False)
    ID_card = db.Column(db.String(20), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<{User}: {self.username}>'

class EmailVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey("User.id"))
    token = db.Column(db.String(44), nullable=False)
    expires_at = db.Column(db.DateTime, nullabl=False)

#base class: Registration Plates, Parking Operator queries here, these are the common attributes of all types of services,
# if not in table -> car should be fined
class ActiveRegistrationPlate(db.Model):
    __tablename__ = "active_users"
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey("User.id"))
    vehicle_reg_plate = db.Column(db.String(20), unique=True, nullable=False)
    registered_parking_zone = db.Column(db.String(5), nullable=False)
    fined = db.Column(db.Boolean, default=False)

#ShortTerm  metering - which user, how much hours should be billed
class HourlyParkingInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    check_in = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(Skopje_TZ), nullable=False)



# Monthly subs - once a user is written in this table, only payed_for_month=True/False is updated monthly
# Schedule: when payed_for_month = True (at the beginning of the month), remove the user from ActiveRegistrationPlates and
# set to False
class MonthlySub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    payed_for_month = db.Column(db.Boolean, default = False)
    last_updated = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(Skopje_TZ), onupdate=lambda: datetime.now(Skopje_TZ), nullable=False)

#This table has no function in the REST API, only for analytics
class Resident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    registration_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(Skopje_TZ), nullable=False)

##might be obsolete, merge with base, check if any business logic differences exist between sms users and guests
class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, unique=True, nullable=False)

class Operator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

#class ParkingZones(db.Model):
    #__tablename__ = "zones"
   # id = db.Column(db.Integer, primary_key=True)
   # zone = db.Column(db.String(20), unique=True, nullable=False)
   # rate = db.Column(db.Integer(20), unique=True, nullable=False)
#zones = ["Z1": ,"Z2": ]


#class GuestCard(db.Model):