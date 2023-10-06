
from flask import Blueprint, jsonify, request, current_app as app
import pandas as pd
from decorators.decorators import  premium_required, print_full_exception, token_required, error_handler
import utils.utils as utils
from ai import generate_quiz
from firestore.firestore_db import UnprotectedFirestoreDB
quizzes_bp = Blueprint('quizzes', __name__)


@quizzes_bp.route("/create-quiz/", endpoint="create_quiz", methods=['POST'])
@token_required
@error_handler
@premium_required('quiz')
def create_quiz():
    utils.abort_if_already_ai_generating()
    quiz = create_quiz_(request.json['tid'])
    return jsonify(quiz), 200


@quizzes_bp.route("/get-quizzes/<tid>", endpoint="get_quizzes", methods=['GET'])
@token_required
@error_handler
def get_quizzes(tid):
    db = app.config['db']
    quizzes = db.get("quizzes", where=('tid', '==', tid), order_by=('created_on', 'ASCENDING'))
    for quiz in quizzes:
        quiz = process(quiz)
    
    return jsonify({"quizzes": quizzes}), 200

@quizzes_bp.route("/submit-quiz/", endpoint="submit_quiz", methods=['POST'])
@token_required
@error_handler
def submit_quiz():
    db = app.config['db']
    recap = compute_quiz_results(request.json)
    if not (db.user.isAnonymous):
        update_user_quiz_results(recap)
    return jsonify(recap), 200


@quizzes_bp.route("/delete-quiz/<quiz_id>", endpoint="delete_quiz", methods=['DELETE'])
@token_required
@error_handler
def delete_quiz(quiz_id):
    db = app.config['db']
    db.delete("quizzes", quiz_id)
    return jsonify({"message": "Quiz deleted"}), 200


def create_quiz_(tid, test=False):
    db = app.config['db'] if not test else UnprotectedFirestoreDB()
    existing_quizzes = db.get("quizzes", where=('tid', '==', tid))
    if(len(existing_quizzes) > 3):
        return jsonify({"message": "You've reached the maximum number of quizzes for this timeline"}), 400
    
    if(test == False):
        db.user.update_ai_tracking_status('quiz', True)
    try:
        events = db.get('events', where=('tid', '==', tid))
        quiz = generate_quiz.main(events)
        quiz['tid'] = tid
        if(test == False):
            db.user.update_ai_tracking_status('quiz', False, quiz)
        db.add('quizzes', quiz)
    except Exception as e:
        print_full_exception(e)
        if(test == False):
            db.user.update_ai_tracking_status('quiz', False)
        raise Exception("Error generating quiz")

    
    quiz = db.get("quizzes", where=('tid', '==', tid), order_by=('created_on', 'DESCENDING'))[0]
    quiz = process(quiz)

def process(quiz):
    quiz['options'] = [list(option.values()) for option in quiz['options']]
    # quiz['questions'] = quiz['questions'][0:3]
    map_with_user_existing_results(quiz)
    return quiz

def map_with_user_existing_results(quiz):
    try:
        db = app.config['db']
    except:
        db = UnprotectedFirestoreDB()
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
