from flask import flash, redirect, url_for
from flask_login import login_user
from parkingapp.extensions import db
from parkingapp.models.models import User, EmailVerification
from flask_restful import reqparse
import secrets
from parkingapp.auth.email_verification import send_email
from datetime import datetime, timedelta
import traceback
import re


def create_user(args):

    password = args["password"].strip()
    username = args["username"].strip()
    email = args["email_address"].strip()

    if db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none():
        return {'message': 'Username already taken'
                }, 400
    if db.session.execute(db.select(User).where(User.email_address == email)).scalar_one_or_none():
        return {'message': 'Email already taken'
                }, 400
    if len(password) < 12 or len(password) > 30:
        return {'message': 'Passwords should be between 12 and 30 characters long'
                }, 400
    if len(username) < 4 or len(username) > 30:
        return {'message': 'Username length should be between 4 and 30 characters long'
                }, 400
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        return {'message': 'Please enter a valid e-mail address'
                }, 400
    user = User(
        username=args["username"].strip(), name_surname=args["name_surname"].strip(), address=args["address"].strip(),
        email_address=args["email_address"].strip().lower(), ID_card=args["ID_card"], phone_number=args["phone_number"]
    )
    user.set_password(args["password"])
    db.session.add(user)
    db.session.flush()

    ##email verification###
    token = secrets.token_urlsafe(32)
    verification = EmailVerification(user_id=user.id, token=token, expires_at=datetime.utcnow() + timedelta(hours=24))
    try:
        send_email(user.email_address, token)
        db.session.add(verification)
        print("User commited to db")
        db.session.commit()

        return {"message": "A verification link has been sent to your e-mail", "user_id": user.id,
            "email": user.email_address
            }, 201

    except Exception as e:

        db.session.rollback()
        print("Error during email:", e)
        traceback.print_exc()
        return {"message": "Failed to send a verification link to your email"
                }, 400

def verify_email(token_received):
    pending_user = db.session.execute(
        db.select(EmailVerification).where(EmailVerification.token == token_received)).scalar_one_or_none()
    if not token_received or not pending_user:
        return {"message": "Invalid token"
                }, 400
    user = pending_user.user
    if not user:
        # should never happen (DB invariant)
        return {"message": "We couldn't verify your account. Please request a new verification email."
                }, 400

    if pending_user.expires_at < datetime.utcnow():
        return {"message": "Your token has expired"
                }, 200
    user.is_verified = True
    try:
        db.session.delete(pending_user)
        db.session.commit()

    except Exception:
        db.session.rollback()
        return {"message": "Verification failed, please try again."}, 500

    flash("Account is now verified, please log in again")
    return redirect("/login-page")

def user_login(args):

    password = args["password"].strip()
    username = args["username"].strip()
    user = db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none()

    if not user or not user.check_password(password):
        return {"message": "Invalid username or password"
                }, 401
    login_user(user)

    if not user.is_verified:
        return {
            "message": "Account not verified",
            "redirect": url_for("pages.verify")
        }, 403

    return {
        "message": "Login successful",
    }, 200

