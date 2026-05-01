from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate=Migrate()

def create_app():

    app = Flask(__name__, template_folder = "templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_data.db'
    app.config["SECRET_KEY"] = "SOME KEY"

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    from parkingapp.Models.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from parkingapp.Routes.pages import pages
    app.register_blueprint(pages)

    from parkingapp.Routes.rest_routes import api_bp
    app.register_blueprint(api_bp)


    return app