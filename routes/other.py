from flask import Blueprint, jsonify, request
from decorators import token_required, generic_error_handler
from google.cloud import error_reporting
from utils.events import get_google_images

other_bp = Blueprint('other', __name__)

def get_error_reporting_client():
    try:
        client = error_reporting.Client()
    except:
        client = error_reporting.Client.from_service_account_json('secrets/timelime-dev-sa.json')
    return client

@other_bp.route("/report_error", endpoint="report_error", methods=['POST'])
@token_required
@generic_error_handler
def report_error():

    client = get_error_reporting_client()

    try:
        raise Exception(request.json['data']['message'] + "\n " + request.json['data']['stack'])
    except Exception as e:
        client.report_exception()

    return jsonify({"message": "Error reported"}), 200


@other_bp.route("/google-imgs", endpoint="google_images", methods=['POST'])
@token_required
@generic_error_handler
def google_images():
    links = get_google_images(request.json['query'])
    return jsonify({"links": links}), 200