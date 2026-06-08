from flask import session
from parkingapp.extensions import db
from parkingapp.models.models import ActiveRegistrationPlate
from parkingapp.pricing.price_list import ZONE_RATES
import re
from parkingapp.services.input_validation import valid_plates

def plate_check(args):

    plate = args["plate"].strip()
    zone = session.get("operator_zone")
    if not plate:
        return {"message": "Please enter a registration plate"}
    if not zone:
        return {"message": "Operator zone not set"}, 403

    error = valid_plates(plate)
    if error:
        return error

    registered_plate = db.session.execute(db.select(ActiveRegistrationPlate).where(ActiveRegistrationPlate.vehicle_reg_plate == plate)).scalar_one_or_none()

    if not registered_plate:
        return {"message": "The vehicle is not registered in our system. Fine the Subject"}, 403

    current_zone = (registered_plate.registered_parking_zone or "").strip()

# The vehicle could be registered, but not in the zone it is parked
    if current_zone.lower() != zone.lower():
        return {"message": "The vehicle is not registered in the current zone. Fine the Subject"}, 404

    return {"message": "OK"}, 200



valid_zones = {zone["zone"] for zone in ZONE_RATES}

# Operator sets the zone he is currently checking
def change_zone(args):

    zone = args["zone"].strip()

    error = valid_plates(zone)
    if error:
        return error

    session["operator_zone"] = zone

    return {"message":"Parking zone changed successfully"}, 200