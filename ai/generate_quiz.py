from utils.utils import get_secret, print_full_exception
import openai
import pandas as pd
import time

def main(timelineName, events):
    start = time.time()
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
    name = timelineName.lower().replace(' ', '-')
    try:
      obj = eval(resp)
      if(type(obj) == dict):
          obj = obj[list(obj.keys())[0]]
      df = pd.DataFrame(obj)
      df.to_csv(f'ai/generated/quizzes/quiz-{name}.csv', index=False)
    except Exception as e:
      print_full_exception(e)
      with open(f'ai/generated/quizzes/quiz-{name}.txt', 'w') as f:
        f.write(resp)
      raise Exception('Could not parse response')
