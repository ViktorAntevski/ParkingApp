from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask_mail import Message
import os

def send_email(to_email, token):
    verification_link = f"http://127.0.0.1:5000/verify-email?token={token}"
##//skopjeparking.duckdns.org
    msg = Mail(
        from_email=os.getenv("MAIL_DEFAULT_SENDER"),
        to_emails=to_email,
        subject="Verify your email",
        html_content = f"""
<h2>Verify your account</h2>
<p>Click the link below to verify your account:</p>
<a href="{verification_link}">{verification_link}</a>

<p>If you did not sign up, you can ignore this email.</p>

Best regards,
ParkingApp Team
"""
    )
    try:
        sg=SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(msg)
        print("Verification email sent. Please check your inbox (and spam folder if needed).",response.status_code)
    except Exception as e:
        print("SendGrid error:",e)