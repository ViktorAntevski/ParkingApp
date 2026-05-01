from parkingapp import db


#base class: RegistrationPlates, operator queries here
class RegistrationPlates(db.Model):
    __tablename__ = "current_users"
    id = db.Column(db.Integer, primary_key=True)
    vehicle_reg_plate = db.Column(db.String(20), unique=True, nullable=False)
    registered_parking_zone = db.Column(db.String(5), nullable=False)
    fined = db.Column(db.Boolean, default=False)

#subtype tables
class ShortTermParking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, foreign_key="current_users.id")
    username = db.Column(db.String(20), unique=True, nullable=False)
    check_in = db.Column(db.Datetime(timezone=True), default=lambda: datetime.now(Skopje_TZ), nullable=False)

class MonthlySubs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, foreign_key="current_users.id")
    username = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    name_surname = db.Column(db.String(50), nullable=False)
    ID_card = db.Column(db.String(20), nullable=False)
    payed_for_month = db.Column(db.Boolean, default = False)

class Residents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, foreign_key="current_users.id")
    username = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    name_surname = db.Column(db.String(50), nullable=False)
    ID_card = db.Column(db.String(20), nullable=False)

#might be obsolete, merge with base, check if any business logic differences exist between sms users and guests
class Guests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plates_id = db.Column(db.Integer, unique=True, nullable=False)

class Operators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_surname = db.Column(db.String(50), nullable=False)
    ID_card = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

class GuestCards(db.Model):