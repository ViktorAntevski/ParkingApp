from flask import Flask
from parkingapp.extensions import db, migrate, login_manager, bcrypt, mail
from parkingapp.config import MailConfig
from dotenv import load_dotenv
import os


def create_app():

    app = Flask(__name__, template_folder = "templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_data.db'

    load_dotenv()
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config.from_object(MailConfig)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    from parkingapp.auth.user_loader import register_user_loader

    register_user_loader(login_manager)


    from parkingapp.routes.web.auth_web import pages
    from parkingapp.routes.web.user_web import dashboard
    from parkingapp.routes.web.operator_web import operator_dashboard
    from parkingapp.routes.api.user_API import user_api_bp
    from parkingapp.routes.api.operator_API import operator_api_bp
    from parkingapp.routes.api.user_auth_API import user_auth_api_bp
    from parkingapp.routes.api.operator_auth_API import operator_auth_api_bp

    app.register_blueprint(pages)
    app.register_blueprint(dashboard)
    app.register_blueprint(operator_dashboard)
    app.register_blueprint(user_api_bp)
    app.register_blueprint(operator_api_bp)
    app.register_blueprint(user_auth_api_bp)
    app.register_blueprint(operator_auth_api_bp)

    return app