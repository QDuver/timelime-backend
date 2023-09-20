import openai
import pandas as pd
import time
import ai

from utils.utils import get_secret, save_df_to_storage, save_text_to_storage

def main(timelineName, n_events):

  start = time.time()
  name = timelineName.lower().replace(' ', '-')

  # try:
  #   df = pd.read_csv('ai/generated/timelines/'+name+'.csv', index_col=False, dtype=str)
  #   return
  # except:
  #   pass

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

  print('time to generate', n_events, 'events', time.time() - start)
  resp = response['choices'][0]['message']['content']

  try:
    obj = eval(resp)
    if(type(obj) == dict):
      obj = obj[list(obj.keys())[0]]
    df = pd.DataFrame(obj)
    return df
  except:
    df = ai.reprocess.main(name, resp, 'timelines')
    return df
