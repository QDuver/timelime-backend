import time
from flask import Blueprint, jsonify, request, current_app as app
from decorators.decorators import token_required, generic_error_handler
from google.cloud import error_reporting
from utils.methods import get_google_images
from ai import generate_quiz, process_quiz
import utils.utils as utils
import logging
logger = logging.getLogger('my_logger')

other_bp = Blueprint('other', __name__)

def get_error_reporting_client():
    try:
        client = error_reporting.Client()
    except:
        client = error_reporting.Client.from_service_account_json('secrets/GCP_CREDENTIALS.json')
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
    links = get_google_images(request.json['eventName'], request.json['timelineName'])
    return jsonify({"links": links}), 200


@other_bp.route("/create-quiz/", endpoint="create_quiz", methods=['POST'])
@token_required
# @generic_error_handler
def create_quiz():
    db = app.config['db']
    utils.abort_if_already_ai_generating()
    tid = request.json['tid']
    estimated_time = request.json['estimatedTime']
    start_time = time.time()
    existing_quizzes = db.get("quizzes", where=('tid', '==', tid))
    if(len(existing_quizzes) > 3):
        return jsonify({"message": "You've reached the maximum number of quizzes for this timeline"}), 400
    
    db.edit('users', db.authedUser['uid'], {'generating': {'quiz': {'loading': True, 'estimatedTime': -1 }}})
    try:
        timelineName = db.get('timelines', doc=tid)['name']
        events = db.get('events', where=('tid', '==', tid))
        generate_quiz.main(timelineName, events)
        quiz = process_quiz.main( timelineName)
        quiz['tid'] = tid
        quiz['estimated_time'] = estimated_time
        quiz['generation_time'] = time.time() - start_time
        db.edit('users', db.authedUser['uid'], {'generating': {'quiz': {'loading': False, 'estimatedTime': None, 'generated': quiz }}})
        db.add('quizzes', quiz)
    except Exception as e:
        utils.print_full_exception(e)
        db.edit('users', db.authedUser['uid'], {'generating': {'quiz': {'loading': False, 'estimatedTime': None, 'generated': None }}})
        return jsonify({"message": "Error generating quiz"}), 400
    
    quiz = db.get("quizzes", where=('tid', '==', tid), order_by=('created_on', 'DESCENDING'))[0]
    quiz = process(quiz)
    return jsonify(quiz), 200


@other_bp.route("/get-quizzes/<tid>", endpoint="get_quizzes", methods=['GET'])
@token_required
@generic_error_handler
def get_quizzes(tid):
    logging.debug('coucou')
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
    if not (db.is_anonymous_user()):
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
    del quiz['answer']
    quiz['questions'] = quiz['questions']
    quiz['options'] = [list(option.values()) for option in quiz['options']]
    map_with_user_existing_results(quiz)
    return quiz

def map_with_user_existing_results(quiz):
    db = app.config['db']
    try:
        quiz['user_results'] = db.get("users", app.config['user']['uid'])['quiz_results'][quiz['id']]
    except:
        quiz['user_results'] = None


def update_user_quiz_results(recap):
    db = app.config['db']
    try:
        results = db.get("users", app.config['user']['uid'])['quiz_results']
    except:
        results = {}
    results[request.json['quizId']] = {'correct': recap['correct'], 'total': recap['total']}
    db.edit("users", app.config['user']['uid'], {'quiz_results': results})


def compute_quiz_results(data):
    db = app.config['db']
    quiz = db.get("quizzes", data['quizId'])
    results = []
    answers = quiz['answer']
    userAnswers = data['userAnswers']
    for i in range(len(userAnswers)):
        results.append(answers[i] == userAnswers[i])

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
