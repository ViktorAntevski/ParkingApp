from parkingapp.extensions import db
from parkingapp.services.input_validation import valid_plates,valid_parking_zone,duplicate_plates
from flask_login import current_user
from parkingapp.models.models import ActiveRegistrationPlate,HourlyParkingInvoice, Resident
from datetime import datetime
from zoneinfo import ZoneInfo
from parkingapp.pricing.price_list import ZONE_RATES
from flask import session, request, redirect
import stripe
from parkingapp.pricing.currency_conversion import mkd_to_eur_cents
import logging
import traceback

##Stripe max hold amount
MAX_HOLD_AMOUNT: 2000

### Currency rates
EUR_to_MKD = 61.5
MKD_to_EUR = 1/61.5

Skopje_TZ = ZoneInfo("Europe/Skopje")



def parking_start(args):

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


    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",

            payment_intent_data={
                "capture_method": "manual"
            },

            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": f"Parking hold for {plates}",
                    },
                    "unit_amount": 2000,
                },
                "quantity": 1,
            }],

            metadata={
                "plates": plates,
                "zone": zone,
                "user_id": str(user_id)
            },

            success_url="http://localhost:5000/dashboard/api/hourly-parking-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:5000/dashboard?message=Payment+cancelled"
        )

        return {"checkout_url": session.url}, 200

    except:

        return {
            "message": "Unable to start parking. Please try again."
        }, 500


def parking_finalize():

    session_id = request.args.get("session_id")
    print(session_id)

    if not session_id:
        return {"message": "Invalid request"}, 400

    try:
        stripe_session = stripe.checkout.Session.retrieve(session_id)
        print(stripe_session)
        metadata = stripe_session.metadata
        print(metadata)

        plates = metadata["plates"]
        zone = metadata["zone"]
        user_id = int(metadata["user_id"])

        print(plates,zone,user_id)

        payment_intent_id = stripe_session.payment_intent
        print(payment_intent_id)

        if not plates or not zone or not user_id or not payment_intent_id:
            return {"message": "Invalid session data"}, 400

        existing = db.session.execute(
            db.select(HourlyParkingInvoice).where(
                HourlyParkingInvoice.payment_intent_id == payment_intent_id
            )
        ).scalar_one_or_none()
        print(existing)

        if existing:
            return redirect("/dashboard")


        parking = ActiveRegistrationPlate(user_id=user_id, vehicle_reg_plate=plates,registered_parking_zone=zone)
        invoice = HourlyParkingInvoice(user_id=user_id, vehicle_reg_plate=plates, payment_intent_id=payment_intent_id, payment_status="authorized")

        db.session.add(parking)
        db.session.add(invoice)
        db.session.commit()
        print("commit reached")
        session["plates"] = plates

        return redirect("/dashboard")

    except Exception as e:

        db.session.rollback()
        traceback.print_exc()
        logging.error(f"Parking success endpoint failed: {str(e)}")

        return {
            "message": "Failed to start parking. Please try again."
        }, 500


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
    total_invoice = h_rate * total_hours
    invoice_euro = mkd_to_eur_cents(total_invoice)
    print(invoice_euro)


    try:
        stripe.PaymentIntent.capture(
            invoice.payment_intent_id,
            amount_to_capture=invoice_euro
        )
        invoice.payment_status = "captured"
        print("captured")

    except stripe.error.StripeError as e:
        db.session.rollback()
        return {
            "message": f"Stripe error: {str(e)}"
        }, 500

    except Exception as e:
        db.session.rollback()
        return {
            "message": f"Unexpected error: {str(e)}"
        }, 500

    try:
        db.session.delete(active)
        db.session.commit()

        session.pop("plates", None)

    except Exception:
        db.session.rollback()
        print(f"CRITICAL: Payment capture succeeded, but DB failed. Intent: {invoice.payment_intent_id}")
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