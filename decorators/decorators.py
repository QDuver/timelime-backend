
import time
from flask import jsonify, request, current_app as app
from firebase_admin import auth
import hashlib
import hmac
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models.user import User
from utils.constants import DEFAULT_QUOTAS
from utils.utils import print_full_exception

limiter = Limiter( get_remote_address, default_limits=["10 per second"] )

def premium_required(type_):
    def decorator(route_function):
        def wrapper(*args, **kwargs):
            db = app.config['db']
            if not(db.user.isPremium):
                return jsonify({"message": "Premium subscription required"}), 403
            else:
                if(db.user.quotas[type_] <= 0):
                    return jsonify({"message": "Your have exceeded your monthly quota for this feature"}), 403
            return route_function(*args, **kwargs)
        return wrapper
    return decorator

def token_required(route_function):

    def decorated_function(*args, **kwargs):
        User(request)

        return route_function(*args, **kwargs)
    
    return decorated_function

def generic_error_handler(func):
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print_full_exception(e)
            return jsonify('Something went wrong, please try again later'), 500  # Return a 500 Internal Server Error
    return decorator


def add_quotas(user):
    if('quotas' not in user):
        user['quotas'] = DEFAULT_QUOTAS
    return user