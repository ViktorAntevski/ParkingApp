from parkingapp.extensions import mail
from flask_mail import Message

def send_email(to_email, token):
    verification_link = f"http://localhost:5000/verify-email?token={token}"

    msg = Message(
        subject="Verify your email",
        sender = "vantevski1@gmail.com",
        recipients=[to_email]
    )

    msg.body = f"""
Hi,

Please click the link below to verify your account:

{verification_link}

If you did not sign up, you can ignore this email.

Best regards,
ParkingApp Team
"""

    mail.send(msg)