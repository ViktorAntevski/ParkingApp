from parkingapp.extensions import db
from parkingapp.services.input_validation import valid_plates,valid_parking_zone,duplicate_plates
from flask_login import current_user
from parkingapp.models.models import ActiveRegistrationPlate,HourlyParkingInvoice, Resident
from datetime import datetime
from zoneinfo import ZoneInfo
from parkingapp.pricing.price_list import ZONE_RATES
from flask import session

Skopje_TZ = ZoneInfo("Europe/Skopje")

def hourly_parking(args):
    user_id = current_user.id

    zone = args["parking_zone"]
    plates = args["plates"]

    error = valid_parking_zone(zone)
    if error:
        return error

    error = valid_plates(plates)
    if error:
        return error

    error = duplicate_plates(plates)
    if error:
        return error

    parking = ActiveRegistrationPlate(user_id=user_id, vehicle_reg_plate=plates,registered_parking_zone=zone)
    invoice = HourlyParkingInvoice(user_id=user_id, vehicle_reg_plate=plates)

    session["plates"] = plates
    db.session.add(parking)
    db.session.add(invoice)
    db.session.commit()

    return {"message": "Hourly parking started successfully"
            }, 201

def stop_hourly_parking(args):

    plates = args["plates"]

    active = db.session.execute(db.select(ActiveRegistrationPlate).where(
        ActiveRegistrationPlate.vehicle_reg_plate == plates
    )).scalar_one_or_none()

    invoice = db.session.execute(
        db.select(HourlyParkingInvoice)
        .where(HourlyParkingInvoice.vehicle_reg_plate == plates)
    ).scalar_one_or_none()

    if not invoice or not active:
        return {
            "message": "No active invoice found"
        }, 500

    now = datetime.now(Skopje_TZ)
    check_in = invoice.check_in.replace(tzinfo=Skopje_TZ)
    duration = now - check_in

    total_hours = int(duration.total_seconds() // 3600)

    zone = active.registered_parking_zone
    h_rate = None

    for r in ZONE_RATES:
        if r["zone"] == zone:
            h_rate = r["h_rate"]
            break

    if h_rate is None:
        return {"message": "Invalid parking zone for billing"
                }, 500

    if total_hours == 0:
        total_hours = 1
    total_invoice = (h_rate) * total_hours

    try:
        db.session.delete(active)
        db.session.delete(invoice)
        print(total_hours, total_invoice)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return {"message": "Failed to stop parking"
                }, 500

    return {
        "message": f"Parking stopped successfully, The total cost of the parking service is {total_invoice} denars"
    }, 201

def register_resident(args):

    user_id = current_user.id
    plates = args["plates"]
    zone = args["zone"]

    error = valid_parking_zone(zone)
    if error:
        return error

    error = valid_plates(plates)
    if error:
        return error

    error = duplicate_plates(plates)
    if error:
        return error

    plates_written_in_sys = ActiveRegistrationPlate(vehicle_reg_plate=plates, user_id=user_id,registered_parking_zone=zone)
    resident = Resident(vehicle_reg_plate=plates, user_id=user_id)
    db.session.add(plates_written_in_sys)
    db.session.add(resident)
    db.session.commit()
    return {
        "message": "Your vehicle registration is pending. Please go to your nearest ParkingApp office and confirm your identity"
        }, 201