
import flask
from flask import jsonify, request, current_app
import firebase_admin
from firebase_admin import auth
import hashlib
import hmac
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,  # use the remote address of the client as the key to track
    default_limits=["10 per second"]  # set the limit
)

def token_required(route_function):

    def decorated_function(*args, **kwargs):

        if('X-Allow-Unauthorized' in request.headers):  

            secret_key = 'j8qxnvu7crbtc54dyi98'
            uid = request.headers['X-Allow-Unauthorized']
            hmac_hash = hmac.new(secret_key.encode('utf-8'), uid.encode('utf-8'), hashlib.sha256)
            if(hmac_hash.hexdigest() == request.headers['Authorization'].split(" ")[1]):
                user = {'uid': uid, 'isAnonymous': True}
                current_app.config['db'].set_user(user)
                current_app.config['user'] = user
                return route_function(*args, **kwargs)
            else:
                return jsonify({"message": 'Unauthorized'}), 401

        try:
            token = request.headers.get("X-Forwarded-Authorization") if 'X-Forwarded-Authorization' in request.headers else request.headers.get("Authorization")
            decoded_token = auth.verify_id_token(token.split(" ")[1])
        except Exception as e:
            if('Token expired' in str(e)):
                return jsonify({"message": 'Token expired'}), 401
            else:
                return jsonify({"message": 'Unauthorized'}), 401
            
        if not token or not decoded_token:
            return jsonify({"message": "Invalid token"}), 401

        try:
            current_app.config['user'] = current_app.config['db'].get("users", where=('uid', '==', decoded_token['uid']))[0]
        except Exception as e:
            firebase_user = auth.get_user(decoded_token['uid']).__dict__['_data']
            firebase_user['uid'] = firebase_user['localId']
            keys = ['email', 'displayName', 'photoUrl', 'uid']
            user = {key: firebase_user[key] for key in keys if key in firebase_user}
            current_app.config['db'].add("users", user, doc_id=user['uid'])
            current_app.config['user'] = user

        current_app.config['db'].set_user(current_app.config['user'])


        return route_function(*args, **kwargs)
    
    return decorated_function

def generic_error_handler(func):
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e, flush=True)
            response = {
                'error': True,
                'message': str(e),
            }
            return jsonify(response), 500  # Return a 500 Internal Server Error
    return decorator