import openai
import pandas as pd
import time

def main(theme, name, n_events):

  start = time.time()
  

  openai.api_key = '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'

  response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
          {"role": "system", "content": f'''Response has to be an array of dictionnaries (JSON), each representing an event, with the following format: name, description, startDate, endDate, endDate being optional.
          Dates can be in YYYY-MM-DD or YYYY-MM or YYYY format.
          '''},
          {"role": "user", "content": f'''
          Generate a historic timeline of {theme},.
          Create about {n_events} events.
           If possible, all periods of time should be equally represented
             '''},
      ]
  )

  resp = response['choices'][0]['message']['content']
  obj = eval(resp)
  if(type(obj) == dict):
    obj = obj[list(obj.keys())[0]]
  df = pd.DataFrame(obj)
  df.to_csv(f'ai/generated/{name}.csv', index=False)
  print('time to generate', n_events, 'events', time.time() - start)
