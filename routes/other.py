from flask import Blueprint, jsonify, request
from decorators import token_required, generic_error_handler
from google.cloud import error_reporting
from googleapiclient.discovery import build
other_bp = Blueprint('other', __name__)

def get_local_credentials():
    return error_reporting.Client.from_service_account_json('secrets/timelime-dev-sa.json')

def get_error_reporting_client():
    try:
        client = error_reporting.Client()
        if('timelime' not in client._credentials.service_account_email):
            client = get_local_credentials()
    except:
        client = get_local_credentials()
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
    API_KEY = "AIzaSyBl9-P8iSKJ_VXNAFnaaFPqb1XNaWVeluI"
    SEARCH_ENGINE_ID = "90d862b25c6fc454e"

    service = build("customsearch", "v1", developerKey=API_KEY)
    result = service.cse().list(q=request.json['query'], cx=SEARCH_ENGINE_ID, searchType="image").execute()
    links = [link for link in result.get("items", [])]
    print(links)
    return jsonify({"links": links}), 200