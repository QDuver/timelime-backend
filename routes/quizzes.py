
from flask import Blueprint, jsonify, request
from utils.decorators import  premium_required, print_full_exception, auth_required, error_handler
from config import db
from utils.quizzes import generate_ai_quiz
quizzes_bp = Blueprint('quizzes', __name__)


@quizzes_bp.route("/create-quiz/", endpoint="create_quiz", methods=['POST'])
@auth_required
@error_handler
@premium_required('quiz')
def create_quiz():
    quiz = create_quiz_(db, request.json['tid'], request.json['lang'],)
    return jsonify(quiz), 200


@quizzes_bp.route("/get-quizzes/<tid>", endpoint="get_quizzes", methods=['GET'])
@auth_required
@error_handler
def get_quizzes(tid):
    quizzes = db.get("quizzes", where=('tid', '==', tid), order_by=('created_on', 'ASCENDING'))
    for quiz in quizzes:
        quiz = process(quiz)
    
    return jsonify({"quizzes": quizzes}), 200

@quizzes_bp.route("/submit-quiz/", endpoint="submit_quiz", methods=['POST'])
@auth_required
@error_handler
def submit_quiz():
    recap = compute_quiz_results(request.json)
    if not (db.user.isAnonymous):
        update_user_quiz_results(recap)
    return jsonify(recap), 200


@quizzes_bp.route("/delete-quiz/<quiz_id>", endpoint="delete_quiz", methods=['DELETE'])
@auth_required
@error_handler
def delete_quiz(quiz_id):
    db.delete("quizzes", quiz_id)
    return jsonify({"message": "Quiz deleted"}), 200


def create_quiz_(tid, lang='en'):
    existing_quizzes = db.get("quizzes", where=('tid', '==', tid))

    if(len(existing_quizzes) > 3):
        return jsonify({"message": "backend.maxNumberOfQuizReached"}), 400
    
    try:
        events = db.get('events', where=('tid', '==', tid))
        quiz = generate_ai_quiz(events)
        quiz['tid'] = tid
        db.add('quizzes', quiz)
    except Exception as e:
        print_full_exception(e)
        raise Exception("Error generating quiz")

    
    quiz = db.get("quizzes", where=('tid', '==', tid), order_by=('created_on', 'DESCENDING'))[0]
    quiz = process(quiz)
    return quiz

def process(quiz):
    quiz['options'] = [list(option.values()) for option in quiz['options']]
    # quiz['questions'] = quiz['questions'][0:3]
    map_with_user_existing_results(quiz)
    return quiz

def map_with_user_existing_results(quiz):
    try:
        quiz['user_results'] = db.get("users", db.uid)['quiz_results'][quiz['id']]
    except:
        quiz['user_results'] = None


def update_user_quiz_results(recap):
    try:
        results = db.get("users", db.uid)['quiz_results']
    except:
        results = {}
    results[request.json['quizId']] = {'correct': recap['correct'], 'total': recap['total']}
    db.edit("users", db.uid, {'quiz_results': results})


def compute_quiz_results(data):
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
        message = 'quiz.quizResultMsg1'
    elif(score > 0.79):
        message = 'quiz.quizResultMsg2'
    elif(score > 0.59):
        message = 'quiz.quizResultMsg3'
    elif(score > 0.39):
        message = 'quiz.quizResultMsg4'
    else:
        message = 'quiz.quizResultMsg5'
    return {'score': score, 'correct': correct, 'total': total, 'message': message, 'errorIndexes': [i for i, x in enumerate(results) if not x]}
