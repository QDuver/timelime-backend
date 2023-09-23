# import openai
# import pandas as pd
from clean_schedule.main import clean_schedule
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.constants import DEFAULT_QUOTAS
import openai
firestore_init.init()
db = UnprotectedFirestoreDB()
from utils.utils import get_secret

openai.api_key = get_secret('OpenAPI')

message1 =f'''
    I've migrated a project with domain https://time-lime.com from Firebase to GCP.
    I've associated the domain to the Cloud Run Frontend Applicaton through GCP's custom domain solution.
    It works, but once in a while, navigating to the domain will render the old application that used to be in Firebase.
    What could be the issue?
    I've done the migration and mapping more than 48 hours ago.
'''

message2 = '''
in python, i'm running this code

client = secretmanager.SecretManagerServiceClient()
response = client.access_secret_version(name='GCP_CREDENTIALS', )

I get the following error:

google.api_core.exceptions.RetryError: Deadline of 60.0s exceeded while calling target function, last exception: 503 failed to connect to all addresses; last error: UNKNOWN: ipv4:142.250.78.202:443: Handshake read failed
'''

response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' '''},
        {"role": "user", "content": message2},
    ]
)

print(response['choices'][0]['message']['content'])




        