from parkingapp.extensions import db
from parkingapp import create_app
from parkingapp.models.models import Operator

app = create_app()

with app.app_context():

    operator = Operator(username="operator")
    password = "operatoronduty123"
    operator.set_password(password)

    db.session.add(operator)
    db.session.commit()