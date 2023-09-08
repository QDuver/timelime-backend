import openai
import pandas as pd

def main(theme, name, n_events):

  openai.api_key = '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'

  response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
          {"role": "system", "content": "You are a historian."},
          {"role": "user", "content": f'''
          Generate a historic timeline of {theme},.
          It has to be in array of dictionnaries (JSON), each representing an event, with the following format: name, description, startDate, endDate. 
          endDate is optional, but make sure you include at least 3 events which contain both startDate and endDate. 
          Dates have to be in either YYYY-MM-DD or YYYY-MM or YYYY format.
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
