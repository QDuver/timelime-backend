
import json
from flask import Blueprint, request, jsonify, current_app as app
from decorators import token_required, generic_error_handler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/auth", endpoint="get_auth")
@token_required
# @generic_error_handler
def get_auth():
    print(app.config['user'], flush=True)
    if(app.config['user']):
        return app.config['user']
    else:
        return jsonify({"message": "User not found"})

@auth_bp.route("/user", methods=['POST'], endpoint="add_user")
@token_required
# @generic_error_handler
def add_user():
    existing_user = app.config['db'].get("users", where=('uid', '==', request.json['uid']))
    if(len(existing_user) > 0):
        return json.dumps(existing_user[0])


    keys = ['email', 'displayName', 'photoURL', 'uid', 'emailVerified']
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

@auth_bp.route("/contact", methods=['POST'], endpoint="contact")
@token_required
@generic_error_handler    
def contact():
    sg = SendGridAPIClient('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')
    message = Mail(
        to_emails="quentin.duverge@gmail.com",
        from_email=Email("quentin.duverge@gmail.com", request.json["email"]),
        subject="Someone contacting you from Timelime",
        html_content= request.json['message']
        )
    sg.send(message)
    return jsonify({"message": "Email sent"})
