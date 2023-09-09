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

# time to generate 5 events 35.14564371109009
# time to generate 10 events 60.15999913215637
# time to generate 10 events 57.04464268684387
# time to generate 25 events 147.50703859329224
# time to generate 75 events 443.57299995422363
# time to generate 1 events 14.509999990463257
# time to generate 10 events 46.63903737068176
# time to generate 10 events 55.96537947654724