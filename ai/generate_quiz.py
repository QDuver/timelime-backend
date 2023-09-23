import ai
from utils.utils import get_secret, save_df_to_storage, save_raw_to_storage
import openai
import pandas as pd
import datetime
from firestore.firestore_db import UnprotectedFirestoreDB
from flask import current_app as app
import re
import ast
pd.set_option('display.max_columns', None)

def process_ai_quiz(df):
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
        
    return quiz

def main(events):
    openai.api_key = get_secret('OpenAPI')
    events = [event for event in events if 'name' in event and 'startDate' in event and event['startDate']]
    events = [{'name': event['name'], 'startDate': event['startDate'], 'endDate': event['endDate'], 'description': event['description']} for event in events]
    n_events = len(events) if len(events) < 10 else 10

    resp = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k-0613",
    messages=[
          {"role": "system", "content": f'''
          Response has to be in JSON format. Each object represents a question, with the following format: question, options, answer.
          '''},
          {"role": "user", "content": f'''
          Given the events provided at the end of the prompt, generate a historical quiz with {n_events} questions, with multiple choice answers (4 options).
          Be as creative as possible, and make sure the questions are not too easy.
          Questions and answers have to leverage all the information provided in the events, in as much fields as possible (name, description, start date, end date).
            {events}
             '''},
      ]
    )

    resp = resp['choices'][0]['message']['content']
    save_raw_to_storage(resp, 'quizzes')
    df = ai.reprocess.interpret_response(resp, 'quizzes')
    save_df_to_storage(df, 'quizzes')
    df = process_ai_quiz(df)
    save_df_to_storage(df, 'quizzes')
    return df