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
         I am trying to implement Facebook Login for Business on my application.
         But on the authentication popup, I am only seeing on account I have admin access to.
         I know for a fact I have admin access to other accounts.
         '''},
        {"role": "user", "content": msg},
    ]
)

resp = response['choices'][0]['message']['content']
print(resp)



        