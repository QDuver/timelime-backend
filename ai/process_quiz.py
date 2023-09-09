

import pandas as pd
import datetime
from firestore.firestore_db import UnprotectedFirestoreDB
from flask import current_app as app

pd.set_option('display.max_columns', None)
import ast
def main(timeline_id):
    df = pd.read_csv(f'ai/generated/quizzes/quiz-{timeline_id}.csv')
    quiz = {}
    quiz['questions'] = df['question'].tolist()
    quiz['options'] = []
    for i, option  in enumerate(df['options'].tolist()):
        d = {}
        options = ast.literal_eval(option)
        for i, option in enumerate(options):
            d[f'q{i}'] = option
        quiz['options'].append(d)
    quiz['answer'] = df['answer'].tolist()
    quiz['created_on'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    quiz['tid'] = timeline_id
    try:
        db = app.config['db']
        quiz['uid'] = db.authedUser['uid']
    except:
        db = UnprotectedFirestoreDB()
        quiz['uid'] = 'BaxP33wjGCV5iUTKxiPs5b0Bx4c2'
    return quiz
