from utils.utils import get_secret
from firestore.firestore_db import UnprotectedFirestoreDB
import openai
import pandas as pd
import time

def main(timeline_id):
    start = time.time()
    secret = get_secret('OpenAPI')
    openai.api_key = secret
    db = UnprotectedFirestoreDB()
    events = db.get('events', where=('tid', '==', timeline_id))
    events = [event for event in events if 'name' in event and 'startDate' in event and event['startDate']]
    events = [{'name': event['name'], 'startDate': event['startDate'], 'endDate': event['endDate'], 'description': event['description']} for event in events]
    n_events = len(events) if len(events) < 10 else 10

    resp = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
          {"role": "system", "content": "Provide response in JSON format with keys :question, options, answer."},
          {"role": "user", "content": f'''
          Given the following events, generate a historical quiz with {n_events} questions, with multiple choice answers (4 options).
          Be as creative as possible, and make sure the questions are not too easy.
          Questions and answers have to leverage all the information provided in the events, in as much fields as possible (name, description, start date, end date).
            {events}
             '''},
      ]
    )

    resp = resp['choices'][0]['message']['content']
    print('finished generatin quiz', start - time.time())
    obj = eval(resp)
    if(type(obj) == dict):
        obj = obj[list(obj.keys())[0]]
    df = pd.DataFrame(obj)
    df.to_csv(f'ai/generated/quizzes/quiz-{timeline_id}.csv', index=False)

# finished quiz -37.88711762428284
# finished generatin quiz -35.313483476638794