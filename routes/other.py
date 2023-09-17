import time
from flask import Blueprint, jsonify, request, current_app as app
from decorators.decorators import premium_required, token_required, generic_error_handler
from google.cloud import error_reporting
from utils.constants import DEFAULT_QUOTAS
from utils.methods import get_google_images
from ai import generate_quiz, process_quiz
import utils.utils as utils

other_bp = Blueprint('other', __name__)

def get_error_reporting_client():
    try:
        client = error_reporting.Client()
    except:
        client = error_reporting.Client.from_service_account_json('secrets/GCP_CREDENTIALS.json')
    return client

@other_bp.route("/quotas", endpoint="get_quotas", methods=['GET'])
@generic_error_handler
def get_quotas():
    quotas = DEFAULT_QUOTAS
    return jsonify(quotas), 200

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
@premium_required('search')
def google_images():
    links = get_google_images(request.json['eventName'], request.json['timelineName'], 10)
    return jsonify({"links": links}), 200


@other_bp.route("/create-quiz/", endpoint="create_quiz", methods=['POST'])
@token_required
@generic_error_handler
@premium_required('quiz')
def create_quiz():
    db = app.config['db']
    utils.abort_if_already_ai_generating()
    tid = request.json['tid']
    existing_quizzes = db.get("quizzes", where=('tid', '==', tid))
    if(len(existing_quizzes) > 3):
        return jsonify({"message": "You've reached the maximum number of quizzes for this timeline"}), 400
    
    db.user.update_ai_tracking_status('quiz', True)
    try:
        timelineName = db.get('timelines', doc=tid)['name']
        events = db.get('events', where=('tid', '==', tid))
        generate_quiz.main(timelineName, events)
        quiz = process_quiz.main( timelineName)
        quiz['tid'] = tid
        db.user.update_ai_tracking_status('quiz', False, quiz)
        db.add('quizzes', quiz)
    except Exception as e:
        utils.print_full_exception(e)
        db.user.update_ai_tracking_status('quiz', False)
        return jsonify({"message": "Error generating quiz"}), 400
    
    quiz = db.get("quizzes", where=('tid', '==', tid), order_by=('created_on', 'DESCENDING'))[0]
    quiz = process(quiz)
    return jsonify(quiz), 200


@other_bp.route("/get-quizzes/<tid>", endpoint="get_quizzes", methods=['GET'])
@token_required
@generic_error_handler
def get_quizzes(tid):
    db = app.config['db']
    quizzes = db.get("quizzes", where=('tid', '==', tid), order_by=('created_on', 'ASCENDING'))
    for quiz in quizzes:
        quiz = process(quiz)
    
    return jsonify({"quizzes": quizzes}), 200

@other_bp.route("/submit-quiz/", endpoint="submit_quiz", methods=['POST'])
@token_required
@generic_error_handler
def submit_quiz():
    db = app.config['db']
    recap = compute_quiz_results(request.json)
    if not (db.user.isAnonymous):
        update_user_quiz_results(recap)
    return jsonify(recap), 200


@other_bp.route("/delete-quiz/<quiz_id>", endpoint="delete_quiz", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_quiz(quiz_id):
    db = app.config['db']
    db.delete("quizzes", quiz_id)
    return jsonify({"message": "Quiz deleted"}), 200


def process(quiz):
    quiz['options'] = [list(option.values()) for option in quiz['options']]
    # quiz['questions'] = quiz['questions'][0:3]
    map_with_user_existing_results(quiz)
    return quiz

def map_with_user_existing_results(quiz):
    db = app.config['db']
    try:
        quiz['user_results'] = db.get("users", db.uid)['quiz_results'][quiz['id']]
    except:
        quiz['user_results'] = None


def update_user_quiz_results(recap):
    db = app.config['db']
    try:
        results = db.get("users", db.uid)['quiz_results']
    except:
        results = {}
    results[request.json['quizId']] = {'correct': recap['correct'], 'total': recap['total']}
    db.edit("users", db.uid, {'quiz_results': results})


def compute_quiz_results(data):
    db = app.config['db']
    quiz = db.get("quizzes", data['quizId'])
    results = []
    answer = quiz['answer']
    userAnswers = data['userAnswers']
    for i in range(len(userAnswers)):
        results.append(answer[i] == userAnswers[i])

    score = results.count(True) / len(results)
    correct =  results.count(True)
    total = len(results)
    message = ''
    if(score == 1):
        message = 'Great work! You got them all right!'
    elif(score > 0.79):
        message = 'Great work! You almost got them all right!'
    elif(score > 0.59):
        message = 'Good job! You got more than half of them right!'
    elif(score > 0.39):
        message = 'Nice try! You got some of them right!'
    else:
        message = 'You can do better! Study the timeline and try again!'
    return {'score': score, 'correct': correct, 'total': total, 'message': message, 'errorIndexes': [i for i, x in enumerate(results) if not x]}
