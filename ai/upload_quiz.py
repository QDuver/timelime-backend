

import pandas as pd
import datetime
from firestore.firestore_db import UnprotectedFirestoreDB
pd.set_option('display.max_columns', None)
import ast
def main(timeline_id):
    df = pd.read_csv('ai/generated/quiz-9L4uPocMUPJUtuv797vn.csv')
    print(df)
    # for i, row in df.iterrows():
        # print(row['options'])
    quiz = {}
    quiz['questions'] = df['question'].tolist()
    quiz['options'] = [option.replace("'", '"') for option in df['options'].tolist()]
    print(quiz['options'])
    quiz['answer'] = df['answer'].tolist()
    quiz['created_on'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    quiz['tid'] = timeline_id
    db = UnprotectedFirestoreDB()
    db.add('quizzes', quiz)
    # print(json)