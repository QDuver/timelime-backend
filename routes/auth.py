
import json
from flask import Blueprint, request, jsonify
from utils.decorators import auth_required, error_handler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from models.user import User
import config as c
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/auth", endpoint="authenticate")
@error_handler
def authenticate():
    User(request = request)
    return  json.dumps(c.user.__dict__)


@auth_bp.route("/user", methods=['PUT'], endpoint="edit_user")
@auth_required
@error_handler
def edit_user():
    user = request.json
    del user['isPremium']
    del user['quotas']
    c.db.edit("users", user['uid'], user)
    user = c.db.get("users", user['uid'])
    return user

@auth_bp.route("/contact", methods=['POST'], endpoint="contact")
@auth_required
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