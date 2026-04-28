from parkingapp.parkingapp import create_app, db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo

flask_app = create_app()


Skopje_TZ = ZoneInfo("Europe/Skopje")

from parkingapp.parking_payments import models
from parkingapp.parking_payments import routes

#resources 1: add residents, resource 2: add and modifiy guest cards, resource 3: add SMS user, resource 4: add fined and locked





if __name__ = "__main__":
    flask_app.run(debug = True)