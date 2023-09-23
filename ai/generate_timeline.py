from ai.reprocess import interpret_response
import numpy as np
import openai
import pandas as pd
from firebase_admin import auth
from firestore.firestore_db import UnprotectedFirestoreDB
from flask import current_app as app
from utils import event_methods as events_utils
from utils.utils import get_secret, save_df_to_storage, save_raw_to_storage
from utils.event_methods import vaildate_date, validate_dates, process_date, handle_centuries, handle_decades

import ai

pd.set_option('display.max_columns', None)


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
    df = df.drop_duplicates(subset=['name', 'startDate'], keep='first')
    df = _process_dates(df)


    events = []
    for i, row in df.iterrows():
        # try:
            vaildate_date(row['startDate'])
            vaildate_date(row['endDate'])
            row['endDate'] = validate_dates(row['startDate'], row['endDate'])
            event = {'uid': db.uid, 'name': row['name'], 'startDate': row['startDate'], 'description': row['description'], 'endDate': row['endDate']}
            if(image_association == 'google'):
                event['imageURL'] = events_utils.get_google_images(row['name'], timelineName)[0]
            events.append(event)
        # except Exception as e:
        #     print('error', e, 'could not load event', row.to_dict())
    
    return events
    
def main(timelineName, n_events, image_association = None):

  name = timelineName.lower().replace(' ', '-')

  openai.api_key = get_secret('OpenAPI')

  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k-0613",
    messages=[
          {"role": "system", "content": f'''
          Response has to be in JSON format. Each object represents an event, with the following format: name, description, startDate, endDate, endDate being optional.
          Dates can be in YYYY-MM-DD or YYYY-MM or YYYY format.
          Never write the dates with BC, AD, CE, BCE, ABY, BBY, etc. If they are negative, just put a minus sign before the year.
          Escape all double quotes with a backslash.
          '''},
          {"role": "user", "content": f'''
          Generate a historic timeline of {timelineName}.
          Create about {n_events} events.
           If possible, all periods of time should be equally represented
             '''},
      ]
  )

  resp = response['choices'][0]['message']['content']
  save_raw_to_storage(resp, 'timelines')
  df = interpret_response(resp, 'timelines')
  save_df_to_storage(df, 'timelines')
  df = process_ai_timeline(df, timelineName, image_association)
  save_df_to_storage(df, 'timelines')
  return df


