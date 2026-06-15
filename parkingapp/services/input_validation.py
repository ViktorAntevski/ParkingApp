from parkingapp.extensions import db
from parkingapp.models.models import ActiveRegistrationPlate
import re
from parkingapp.pricing.price_list import ZONE_RATES

VALID_ZONES = {zone["zone"] for zone in ZONE_RATES}


def valid_parking_zone(zone):

    zone=zone.upper()
    if zone not in VALID_ZONES:
        return {"message": "Incorrect parking zone"
                }, 400


def valid_plates(plates):
    pattern = r'^[A-Za-z]{2}[0-9]{4}[A-Za-z]{2}$'
    if not re.match(pattern, plates):
        return {
        "message": "Insert valid plates format"
    }, 400

def duplicate_plates(plates):
    plates_written_in_sys = db.session.execute(
        db.select(ActiveRegistrationPlate).where(ActiveRegistrationPlate.vehicle_reg_plate == plates)).scalar_one_or_none()
    if plates_written_in_sys:
        return {
            "message": "This vehicle is already registered in our system"
        }, 400