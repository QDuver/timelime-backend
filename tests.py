# import openai
# import pandas as pd
from clean_schedule.main import clean_schedule
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from clean_schedule.constants import DEFAULT_QUOTAS
firestore_init.init()
db = UnprotectedFirestoreDB()
# from utils.utils import get_secret

# openai.api_key = get_secret('OpenAPI')

# response = openai.ChatCompletion.create(
# model="gpt-4",
# messages=[
#         {"role": "system", "content": f''' '''},
#         {"role": "user", "content": f'''
#     I've migrated a project with domain https://time-lime.com from Firebase to GCP.
#     I've associated the domain to the Cloud Run Frontend Applicaton through GCP's custom domain solution.
#     It works, but once in a while, navigating to the domain will render the old application that used to be in Firebase.
#     What could be the issue?
    
#     I've done the migration and mapping more than 48 hours ago.


#             '''},
#     ]
# )

# print(response['choices'][0]['message']['content'])


import time
print(time.localtime().tm_mday)


        