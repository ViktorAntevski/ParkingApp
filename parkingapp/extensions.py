from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
import stripe
from config import StripeConfig

login_manager = LoginManager()
mail = Mail()
bcrypt = Bcrypt()
migrate=Migrate()

def init_stripe():
    stripe.api_key = StripeConfig.STRIPE_SECRET_KEY

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db_metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=db_metadata)

