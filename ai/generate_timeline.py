from ai import process
import openai
import pandas as pd

from utils.utils import get_secret

import ai

pd.set_option('display.max_columns', None)

def main(timelineName, n_events, image_association = None):

  openai.api_key = get_secret('OpenAPI')

  resp = openai.ChatCompletion.create(
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

  return process.main(resp, 'timelines', timelineName, image_association)


