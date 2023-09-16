

import pandas as pd
import datetime
from firestore.firestore_db import UnprotectedFirestoreDB
from flask import current_app as app
import re

pd.set_option('display.max_columns', None)
import ast
def main(timelineName):
    name = timelineName.lower().replace(' ', '-')
    df = pd.read_csv(f'ai/generated/quizzes/{name}.csv')
    quiz = {}
    quiz['questions'] = df['question'].tolist()
    quiz['options'] = []
    for i, option  in enumerate(df['options'].tolist()):
        d = {}
        options = ast.literal_eval(option)
        for i, option in enumerate(options):
            d[f'q{i}'] = re.sub(r'^[a-zA-Z]\)\s+', '', option)
        quiz['options'].append(d)
    answer = df['answer'].tolist()
    answer = [re.sub(r'^[a-zA-Z]\)\s+', '', str(a)) for a in answer]
    quiz['answer'] = answer

    quiz['created_on'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        db = app.config['db']
        quiz['uid'] = db.uid
    except:
        db = UnprotectedFirestoreDB()
        quiz['uid'] = 'BaxP33wjGCV5iUTKxiPs5b0Bx4c2'
    return quiz
