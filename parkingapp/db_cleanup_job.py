from parkingapp import db, create_app
from parkingapp.Models.models import EmailVerification, User, ActiveRegistrationPlate, HourlyParkingInvoice
from datetime import datetime

flask_app = create_app()

##clear EmailVerification table of verification requests
#db.session.execute(db.delete(EmailVerification).where(EmailVerification.expires_at < datetime.utcnow()))
##db.session.commit()


##only for dev - Clear user table

with flask_app.app_context():
    db.session.execute(db.delete(User))
    db.session.execute(db.delete(EmailVerification))
    db.session.execute(db.delete(ActiveRegistrationPlate))
    db.session.execute(db.delete(HourlyParkingInvoice))
    print("User table cleared")
    db.session.commit()

