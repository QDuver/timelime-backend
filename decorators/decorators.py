
import flask
from flask import jsonify, request, current_app
import firebase_admin
from firebase_admin import auth
import hashlib
import hmac

def token_required(route_function):

    def decorated_function(*args, **kwargs):

        if('X-Allow-Unauthorized' in request.headers):  

            print('X-Allow-Unauthorized', flush=True)          

            secret_key = 'j8qxnvu7crbtc54dyi98'
            uid = request.headers['X-Allow-Unauthorized']
            hmac_hash = hmac.new(secret_key.encode('utf-8'), uid.encode('utf-8'), hashlib.sha256)
            if(hmac_hash.hexdigest() == request.headers['Authorization'].split(" ")[1]):
                user = {'uid': uid, 'isAnonymous': True}
                print('user', user, flush=True)
                current_app.config['db'].set_user(user)
                print('current_app', current_app.config['db'].authedUser, flush=True)
                current_app.config['user'] = user
                return route_function(*args, **kwargs)
            else:
                return jsonify({"message": 'Unauthorized'}), 401

        try:
            token = request.headers.get("X-Forwarded-Authorization") if 'X-Forwarded-Authorization' in request.headers else request.headers.get("Authorization")
            decoded_token = auth.verify_id_token(token.split(" ")[1])
        except Exception as e:
            print(e, flush=True)
            if('Token expired' in str(e)):
                return jsonify({"message": 'Token expired'}), 401
            else:
                return jsonify({"message": 'Unauthorized'}), 401
            
        if not token or not decoded_token:
            return jsonify({"message": "Invalid token"}), 401

        try:
            current_app.config['user'] = current_app.config['db'].get("users", where=('uid', '==', decoded_token['uid']))[0]
            current_app.config['db'].set_user(current_app.config['user'])
        except Exception as e:
            print('SETTING USER AS NONE')
            print(e, flush=True)
            current_app.config['user'] = None

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