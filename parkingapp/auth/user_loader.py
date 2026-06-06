from functools import wraps
from flask_login import current_user
from flask import abort
from parkingapp.models.models import User, Operator
from flask_login import LoginManager


def register_user_loader(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        try:
            type_, id_ = user_id.split(":")
            id_ = int(id_)
        except (ValueError, AttributeError):
            return None

        if type_ == "user":
            user = User.query.get(id_)
            if user:
                user.user_type = "user"
            return user

        elif type_ == "operator":
            operator = Operator.query.get(id_)
            if operator:
                operator.user_type = "operator"
            return operator

        return None







##### ROLE SEPARATION######
def user_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)

        if not current_user.get_id().startswith("user:"):
            abort(403)

        return f(*args, **kwargs)

    return wrapper


def operator_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)

        if not current_user.get_id().startswith("operator:"):
            abort(403)

        return f(*args, **kwargs)

    return wrapper

