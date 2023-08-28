from flask import Blueprint, jsonify, request
from decorators import token_required, generic_error_handler
from google.cloud import error_reporting
monitoring_bp = Blueprint('monitoring', __name__)

def get_local_credentials():
    return error_reporting.Client.from_service_account_json('secrets/timelime-dev-sa.json')


try:
    client = error_reporting.Client()
    if('timelime' not in client._credentials.service_account_email):
        client = get_local_credentials()
except:
    client = get_local_credentials()

@monitoring_bp.route("/report_error", endpoint="report_error", methods=['POST'])
@token_required
@generic_error_handler
def report_error():

    try:
        raise Exception(request.json['data']['message'] + "\n " + request.json['data']['stack'])
    except Exception as e:
        client.report_exception()

    return jsonify({"message": "Error reported"}), 200


