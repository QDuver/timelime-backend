import openai
import pandas as pd
from utils.utils import get_secret, set_env_variables

set_env_variables()
openai.api_key = get_secret('OpenAPI')

msg = f'''

'''
print(msg)
response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' 
    In Angular SSR, how to know if the user is on an  in-app browser environment? (also known as webview)
         '''},
        {"role": "user", "content": msg},
    ]
)

resp = response['choices'][0]['message']['content']
print(resp)



        