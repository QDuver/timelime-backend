
import logging
import time
import traceback
from flask import jsonify, request, current_app as app
from firebase_admin import auth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models.exceptions import TokenExpired
from models.user import User
from utils.constants import DEFAULT_QUOTAS

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
        start = time.time()
        user = User(request)
        print(time.time() - start, 'token_required', flush=True)
        if(user.token_expired):
            print('TOKEN EXPIRED', flush=True)
            return jsonify({"message": "Token expired"}), 401

        return route_function(*args, **kwargs)
    
    return decorated_function

def generic_error_handler(func):
    def decorator(*args, **kwargs):
        print('generic_error_handler', flush=True)
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

def print_full_exception(e):
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.WARNING)
    error_type = type(e).__name__
    error_message = str(e)
    tb_formatted = ''.join(traceback.format_tb(e.__traceback__))
    log_message = f"\n\nTraceback:\n{tb_formatted}\n\nError Type: {error_type}\nError Message: {error_message}\n\n"
    print('ERROR --------')
    logger.error(log_message)
    print('--------')
