
import json
from flask import Blueprint, request, jsonify, current_app as app
from decorators import token_required, generic_error_handler
import custom_jwt.custom_jwt as custom_jwt

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/auth", endpoint="get_auth")
@token_required
# @generic_error_handler
def get_auth():
    if(app.config['user']):
        return app.config['user']
    else:
        return jsonify({"message": "User not found"})

@auth_bp.route("/unauthed_token", endpoint="get_unauthed_token", methods=['POST'])
@generic_error_handler
def get_auth():
    token = custom_jwt.encode_token(request.headers, request.json['tempUserId'])
    return jsonify({"token": token})

@auth_bp.route("/user", methods=['POST'], endpoint="add_user")
@token_required
# @generic_error_handler
def add_user():
    existing_user = app.config['db'].get("users", where=('email', '==', request.json['email']))
    if(len(existing_user) > 0):
        return json.dumps(existing_user[0])


    keys = ['email', 'displayName', 'photoURL', 'uid']
    user = {key: request.json[key] for key in keys if key in request.json}
    app.config['db'].add("users", user, doc_id=request.json['uid'])
    return json.dumps(user)

@auth_bp.route("/user", methods=['PUT'], endpoint="edit_user")
@token_required
# @generic_error_handler
def edit_user():
    user = request.json
    app.config['db'].edit("users", user['uid'], user)
    return json.dumps(user)