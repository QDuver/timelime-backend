import openai
from utils.utils import get_secret, set_env_variables

set_env_variables()
openai.api_key = get_secret('OpenAPI')

msg = '''
I have my own website called Timelime, and I handle authentication through GCP / Firebase.
Currently when user logs in through Google, the Consent Screen mentions : "Choose an account to continue to timelime-prod.firebaseapp.com"
I want to change this to "Choose an account to continue to Timelime"
'''

response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' '''},
        {"role": "user", "content": msg},
    ]
)

print(response['choices'][0]['message']['content'])




        