from tkinter.constants import CASCADE

from parkingapp import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from parkingapp import bcrypt
import tzdata

#TimeZone
Skopje_TZ = ZoneInfo("Europe/Skopje")


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    name_surname = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    email_address = db.Column(db.String(50), unique=True, nullable=False)
    ID_card = db.Column(db.String(20), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    last_resend = db.Column(db.DateTime)
    ver_token = db.relationship("EmailVerification", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"user:{self.id}"

    def __repr__(self):
        return f'<{User}: {self.username}>'

class EmailVerification(db.Model):
    __tablename__ = "email_verification"
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    token = db.Column(db.String(44), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    user = db.relationship("User", back_populates="ver_token")


#base class: Registration Plates, Parking Operator queries here, these are the common attributes of all types of services,
# if not in table -> car should be fined
class ActiveRegistrationPlate(db.Model):
    __tablename__ = "active_users"
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    vehicle_reg_plate = db.Column(db.String(20), unique=True, nullable=False)
    registered_parking_zone = db.Column(db.String(5), nullable=False)
    hourly_invoice = db.relationship("HourlyParkingInvoice", cascade="all, delete-orphan")
    monthly_subscriber = db.relationship("MonthlySub", cascade="all, delete-orphan")
    resident = db.relationship("Resident", cascade="all, delete-orphan")


#ShortTerm  metering - which user, how much hours should be billed
class HourlyParkingInvoice(db.Model):
    __tablename__ = "parking_invoice"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    check_in = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(Skopje_TZ), nullable=False)
    vehicle_reg_plate = db.Column(db.String(20), db.ForeignKey("active_users.vehicle_reg_plate", ondelete ="CASCADE"), unique=True, nullable=False)



# Monthly subs - once a user is written in this table, only payed_for_month=True/False is updated monthly
# Schedule: when payed_for_month = True (at the beginning of the month), remove the user from ActiveRegistrationPlates and
# set to False
class MonthlySub(db.Model):
    __tablename__ = "monthly_sub"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    vehicle_reg_plate = db.Column(db.String(20), db.ForeignKey("active_users.vehicle_reg_plate", ondelete ="CASCADE"), unique=True, nullable=False)
    payed_for_month = db.Column(db.Boolean, default = False)
    last_updated = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(Skopje_TZ), onupdate=lambda: datetime.now(Skopje_TZ), nullable=False)


class Resident(db.Model):
    __tablename__ = "resident"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    registration_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(Skopje_TZ), nullable=False)
    vehicle_reg_plate = db.Column(db.String(20), db.ForeignKey("active_users.vehicle_reg_plate", ondelete ="CASCADE"), unique=True, nullable=False)
    identity = db.Column(db.Boolean, default=False)
    # identity boolean: a resident should walk up to his nearest office to confirm his identity and home address. The operator there,
    # will set this column to True, and add reg table to ActiveRegistrationPlate.

##might be obsolete, merge with ActiveRegistrationPlate, check if the is any difference in business logic between sms users and guests
class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, unique=True, nullable=False)

class Operator(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"operator:{self.id}"


#class GuestCard(db.Model):