from flask import Blueprint, jsonify, request, current_app as app
from decorators.decorators import token_required, generic_error_handler
from google.cloud import error_reporting
from utils.events import get_google_images

other_bp = Blueprint('other', __name__)

def get_error_reporting_client():
    try:
        client = error_reporting.Client()
        print(client.service_account_email, flush=True)
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


@other_bp.route("/create_quiz/<timeline_id>", endpoint="create_quiz", methods=['GET'])
@token_required
@generic_error_handler
def create_quiz(timeline_id):
    print(timeline_id)
    return jsonify({"timeline_id": timeline_id}), 200


@other_bp.route("/get_quizzes/<timeline_id>", endpoint="get_quizzes", methods=['GET'])
@token_required
@generic_error_handler
def get_quizzes(timeline_id):
    db = app.config['db']
    quizzes = db.get("quizzes", where=('tid', '==', timeline_id), order_by=('created_on', 'ASCENDING'))
    return jsonify({"quizzes": quizzes}), 200