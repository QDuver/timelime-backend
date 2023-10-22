from ai import process, prompts
import openai
import pandas as pd
from utils.utils import get_secret


pd.set_option('display.max_columns', None)

def main(timeline_name, n_events, lang='en', image_association = None):

  prompt = prompts.get_timeline_prompts(n_events, timeline_name)

  openai.api_key = get_secret('OpenAPI')

  resp = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
          {"role": "system", "content": prompt[lang][0]},
          {"role": "user", "content": prompt[lang][1]},
      ]
  )

  return process.main(resp, 'timelines', timeline_name, image_association)


