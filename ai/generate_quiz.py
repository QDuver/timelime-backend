from ai import process, prompts
from utils.utils import get_secret
import openai
import pandas as pd
pd.set_option('display.max_columns', None)




def main(events, lang='en'):
    openai.api_key = get_secret('OpenAPI')
    events = [event for event in events if 'name' in event and 'startDate' in event and event['startDate']]
    events = [{'name': event['name'], 'startDate': event['startDate'], 'endDate': event['endDate'], 'description': event['description']} for event in events]
    n_events = len(events) if len(events) < 10 else 10
    if(n_events < 1):
        raise Exception('No events found in the timeline')

    prompt = prompts.get_quiz_prompts(n_events, events)
    resp = openai.ChatCompletion.create(
    # model="gpt-3.5-turbo",
    model="gpt-4",
    messages=[
          {"role": "system", "content": prompt[lang][0]},
          {"role": "user", "content": prompt[lang][1]},
      ]
    )

    return process.main(resp, 'quizzes', None)

