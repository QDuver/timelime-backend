from flask import Blueprint, jsonify, request, current_app as app
from decorators.decorators import premium_required, token_required, error_handler
from google.cloud import error_reporting
from utils.constants import DEFAULT_QUOTAS

other_bp = Blueprint('other', __name__)

def get_error_reporting_client():
    try:
        client = error_reporting.Client()
    except:
        client = error_reporting.Client.from_service_account_json('secrets/GCP_CREDENTIALS.json')
    return client

@other_bp.route("/quotas", endpoint="get_quotas", methods=['GET'])
@error_handler
def get_quotas():
    quotas = DEFAULT_QUOTAS
    return jsonify(quotas), 200

@other_bp.route("/report_error", endpoint="report_error", methods=['POST'])
@token_required
@error_handler
def report_error():
    client = get_error_reporting_client()
    try:
        raise Exception(request.json['data']['message'] + "\n " + request.json['data']['stack'])
    except Exception as e:
        client.report_exception()

    return jsonify({"message": "Error reported"}), 200





