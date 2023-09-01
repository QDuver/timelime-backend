
import json
from flask import Blueprint, request, jsonify, current_app as app
from decorators.decorators import token_required, generic_error_handler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/auth", endpoint="get_auth")
@token_required
@generic_error_handler
def get_auth():
    return app.config['user']


@auth_bp.route("/user", methods=['PUT'], endpoint="edit_user")
@token_required
@generic_error_handler
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