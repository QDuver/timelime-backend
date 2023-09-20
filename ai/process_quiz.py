

import pandas as pd
import datetime
from firestore.firestore_db import UnprotectedFirestoreDB
from flask import current_app as app
import re

from utils.utils import print_full_exception, save_df_to_storage

pd.set_option('display.max_columns', None)
import ast
def main(df):
    try:
        df = df.head(10)
        df = df.astype(str)
        quiz = {}
        quiz['questions'] = df['question'].tolist()
        quiz['options'] = []
        for i, option  in enumerate(df['options'].tolist()):
            d = {}
            options = ast.literal_eval(option)
            for i, option2 in enumerate(options):
                d[f'q{i}'] = re.sub(r'^[a-zA-Z]\)\s+', '', option2)
            quiz['options'].append(d)
        answer = df['answer'].tolist()
        answer = [re.sub(r'^[a-zA-Z]\)\s+', '', str(a)) for a in answer]
        quiz['answer'] = answer

        quiz['created_on'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        quiz['uid'] = app.config['db'].uid
    except Exception as e:
        print_full_exception(e)
        save_df_to_storage(df, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        raise Exception('Error processing quiz')
        
    return quiz
