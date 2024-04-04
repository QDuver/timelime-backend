
import logging
import traceback
from flask import jsonify, request, current_app as app
from firebase_admin import auth
from models.exceptions import CustomException
from models.user import User
from utils.constants import DEFAULT_QUOTAS
from config import db


def premium_required(type_):
    def decorator(route_function):
        def wrapper(*args, **kwargs):
            if not(db.user.isPremium):
                return jsonify({"message": "backend.premiumSubscriptionRequired"}), 403
            else:
                if(db.user.quotas[type_] <= 0):
                    return jsonify({"message": "backend.monthlyQuotaReached"}), 403
            return route_function(*args, **kwargs)
        return wrapper
    return decorator

def error_handler(func):
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CustomException as e:
            return jsonify({"message": str(e)}), 403
        except Exception as e:
            if( type(e).__name__ == 'RateLimitExceeded' ):
                return jsonify({"message": "backend.tooManyRequests"}), 429
            if('Token expired' in str(e)):
                return jsonify({"message": "backend.sessionExpired"}), 403

            print_full_exception(e)
            return jsonify({"message": 'backend.somethingWentWrong'}), 500  # Return a 500 Internal Server Error
    return decorator

def token_required(route_function):

    def decorated_function(*args, **kwargs):
        User(db, request = request)
        return route_function(*args, **kwargs)
    
    return decorated_function

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
