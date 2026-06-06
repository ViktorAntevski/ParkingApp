from flask import url_for, redirect, jsonify, flash
from functools import wraps
from flask_login import current_user
from flask import abort

##### Role separation enforcement ######

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


###User e-mail verification enforcement ####

def verified_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("pages.login_page"))

        if not current_user.is_verified:
            return redirect(url_for("pages.verify"))

        return f(*args, **kwargs)
    return wrapper