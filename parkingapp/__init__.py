from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from parkingapp.mail_config import Config
from parkingapp.extensions import mail
from sqlalchemy import MetaData
from auth import register_user_loader
from dotenv import load_dotenv
import os

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db_metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=db_metadata)
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate=Migrate()

def create_app():

    app = Flask(__name__, template_folder = "templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_data.db'

    load_dotenv()
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    register_user_loader(login_manager)


    from parkingapp.Routes.pages import pages
    from parkingapp.Routes.user_dashboard import dashboard
    from parkingapp.Routes.user_routes import user_api_bp
    from parkingapp.Routes.operator_routes import operator_api_bp
    app.register_blueprint(pages)
    app.register_blueprint(dashboard)
    app.register_blueprint(user_api_bp)
    app.register_blueprint(operator_api_bp)

    return app