import ast
import datetime
import re
from decorators.decorators import print_full_exception
import openai
import pandas as pd
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.utils import get_secret, save_df_to_storage, save_raw_to_storage
import numpy as np
from flask import current_app as app
from utils import event_methods as events_utils
from utils.event_methods import vaildate_date, validate_dates, process_date, handle_centuries, handle_decades

def main(resp, type_, timelineName, image_association=None):
    resp = resp['choices'][0]['message']['content']
    save_raw_to_storage(resp, type_, 'step1')
    try:
        df = interpret_response(resp)
    except:
        try:
            df = ai_reformating(resp, type_)
        except Exception as e:
            print_full_exception(e)
            raise Exception('Could not parse response')
    save_df_to_storage(df, type_, 'step3')
    if(type_ == 'timelines'):
        generated = process_ai_timeline(df, timelineName, image_association)
    elif(type_ == 'quizzes'):
        generated = process_ai_quiz(df)
    save_df_to_storage(pd.DataFrame(generated), type_, 'step4')
    return generated


def ai_reformating(text, type_):

    if(type_ == 'quizzes'):
        format_ = '{question: string, options: string[], answer: string}'
    elif(type_ == 'timelines'):
        format_ = '{name, description, startDate, endDate}'

    openai.api_key = get_secret('OpenAPI')

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k-0613",
    messages=[
            {"role": "system", "content": f'''
            Response should be a JSON object with the following format: [{format_}, {format_}, ...]
            '''},
            {"role": "user", "content": f'''
            Reprocess the following text so that the response is readable by pandas.read_json without any errors.
            Only provide the response, not other text : 
            {text}
                '''},
        ]
    )

    resp = response['choices'][0]['message']['content']
    save_raw_to_storage(resp, 'quizzes', 'step2')
    try: 
        df = pd.read_json(resp)
        return df
    except:
        try:
            obj = eval(resp)
            df = pd.read_json(obj)
            return df
        except:
            obj = eval(resp)
            obj = obj[list(obj.keys())[0]]
            df = pd.DataFrame(obj)
            return df


def interpret_response(resp):
    obj = eval(resp.strip())
    if(type(obj) == dict):
        obj = obj[list(obj.keys())[0]]
    df = pd.DataFrame(obj)
    return df


def _process_dates(df):
    if not ('endDate' in df.columns):
      df['endDate'] = None
    df['startDate'] = df['startDate'].apply(lambda x: process_date(x))
    df['endDate'] = df['endDate'].apply(lambda x: process_date(x))
    df  = df.apply(lambda x: handle_centuries(x), axis=1)
    df  = df.apply(lambda x: handle_decades(x), axis=1)
    df = df.apply(lambda x: events_utils.strip_leading_zeros(x), axis=1)
    return df

def process_ai_timeline(df, timelineName, image_association = None):
    try:
        db = app.config['db']
    except:
        db = UnprotectedFirestoreDB()
    
    df = df.replace({np.nan: None})
    df = df.astype(str).replace({'none': None}).replace({'None': None})
    df = df.drop_duplicates(subset=['name', 'startDate'], keep='first')
    df = _process_dates(df)

    events = []
    for i, row in df.iterrows():
        try:
            vaildate_date(row['startDate'])
            vaildate_date(row['endDate'])
            row['endDate'] = validate_dates(row['startDate'], row['endDate'])
            event = {'uid': db.uid, 'name': row['name'], 'startDate': row['startDate'], 'description': row['description'], 'endDate': row['endDate']}
            if(image_association == 'google'):
                event['imageURL'] = events_utils.get_google_images(row['name'], timelineName)[0]
            events.append(event)
        except Exception as e:
            print('error', e, 'could not load event', row.to_dict())
    
    return events
    

def process_ai_quiz(df):
    df = df.head(10)
    df = df.astype(str).replace({'none': None}).replace({'None': None})
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