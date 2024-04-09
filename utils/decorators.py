
import logging
from flask import jsonify
import traceback
from models.exceptions import CustomException
import config as c

def premium_required(func):
        def wrapper(*args, **kwargs):
            if ((c.user is None) or (not c.user.isPremium)):
                return CustomException('backend.premiumSubscriptionRequired')
            return func(*args, **kwargs)
        return wrapper

def error_handler(func):
    def wrapper(*args, **kwargs):
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
    return wrapper

def auth_required(func):
    def wrapper(*args, **kwargs):
        if c.user is None:
            raise CustomException("backend.notAuthenticated")
        return func(*args, **kwargs)
    return wrapper

def igore_error_on_prod_but_raise_on_preprod(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if(c.is_prod()):
                pass
            else:
                raise(e)
    return wrapper


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
