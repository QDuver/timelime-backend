
import json
from flask import Blueprint, request, jsonify, current_app as app
from decorators.decorators import token_required, error_handler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from config import db
from models.user import User
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/auth", endpoint="get_auth")
@error_handler
@token_required
def get_auth():
    return  json.dumps(db.user.to_dict())


@auth_bp.route("/user", methods=['PUT'], endpoint="edit_user")
@token_required
@error_handler
def edit_user():
    user = request.json
    del user['isPremium']
    del user['quotas']
    app.config['db'].edit("users", user['uid'], user)
    user = app.config['db'].get("users", user['uid'])
    return user

@auth_bp.route("/contact", methods=['POST'], endpoint="contact")
@token_required
@error_handler    
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