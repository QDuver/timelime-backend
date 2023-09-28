import ai
from ai import process
from ai.process import ai_reformating
from utils.utils import get_secret, save_df_to_storage, save_raw_to_storage
import openai
import pandas as pd
import datetime
from firestore.firestore_db import UnprotectedFirestoreDB
from flask import current_app as app
import re
import ast
pd.set_option('display.max_columns', None)



def main(events):
    openai.api_key = get_secret('OpenAPI')
    events = [event for event in events if 'name' in event and 'startDate' in event and event['startDate']]
    events = [{'name': event['name'], 'startDate': event['startDate'], 'endDate': event['endDate'], 'description': event['description']} for event in events]
    n_events = len(events) if len(events) < 10 else 10
    if(n_events < 1):
        raise Exception('No events found in the timeline')

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

    return process.main(resp, 'quizzes')

