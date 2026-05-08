from flask import Flask
from flask_SQLAlchemy import SQLAlchemy
from flask_migrate import Migrate
from mail_config import Config
from parkingapp.extensions import mail


db = SQLAlchemy()


def create_app():

    app = Flask(__name__, template_folder = "templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite///:parking_data.db'
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    # import blueprints

    migrate = Migrate(app, db)
    return app

