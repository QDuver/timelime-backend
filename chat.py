import openai
from utils.utils import get_secret, set_env_variables

set_env_variables()
openai.api_key = get_secret('OpenAPI')

msg = '''
I have an angular app which I'd like to make available in different languages. 
I'd also like the language to be set based on the browser language, or for the user to change it manually.
How to handle?
'''

response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' '''},
        {"role": "user", "content": msg},
    ]
)

print(response['choices'][0]['message']['content'])




        