from flask import Flask
from flask_SQLAlchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()


def create_app():

    app = Flask(__name__, template_folder = "templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite///:parking_data.db'

    db.init_app(app)

    # import blueprints

    migrate = Migrate(app, db)
    return app

