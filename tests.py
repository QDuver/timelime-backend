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
In Stripe / angular, I have a checkout session that I create with the following code:
const stripe = Stripe('pk_live_xxx');
stripe.redirectToCheckout({ sessionId: res.id});
It doesn't work with the above key, but it work with the pk_test_xxx key.
I've checked the key in the Stripe dashboard and it's the same as the one I'm using.
What could be the issue?  
'''

response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' '''},
        {"role": "user", "content": message2},
    ]
)

print(response['choices'][0]['message']['content'])




        