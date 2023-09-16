
import time
from flask import jsonify, request, current_app as app
from firebase_admin import auth
import hashlib
import hmac
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models.user import User
from utils.constants import QUOTAS
from utils.utils import print_full_exception

limiter = Limiter( get_remote_address, default_limits=["10 per second"] )

def premium_required(route_function):
    def decorated_function(*args, **kwargs):
        if('isPremium' not in app.config['user'] or not app.config['user']['isPremium']):
            return jsonify({"message": "Premium subscription required"}), 403
        return route_function(*args, **kwargs)
    return decorated_function

def token_required(route_function):

    def decorated_function(*args, **kwargs):
        User(request)

        # if('X-Allow-Unauthorized' in request.headers):  

        #     secret_key = 'j8qxnvu7crbtc54dyi98'
        #     uid = request.headers['X-Allow-Unauthorized']
        #     hmac_hash = hmac.new(secret_key.encode('utf-8'), uid.encode('utf-8'), hashlib.sha256)
        #     if(hmac_hash.hexdigest() == request.headers['Authorization'].split(" ")[1]):
        #         user = User(hmac_hash.hexdigest())
        #         print(user, flush=True)
        #         user = {'uid': uid, 'isAnonymous': True}
        #         app.config['db'].set_user(user)
        #         app.config['user'] = user
        #         return route_function(*args, **kwargs)
        #     else:
        #         return jsonify({"message": 'Unauthorized'}), 401

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
        user['quotas'] = QUOTAS
    return user