import openai
import pandas as pd

from utils.utils import get_secret

openai.api_key = get_secret('OpenAPI')

response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' '''},
        {"role": "user", "content": f'''
    I've migrated a project with domain https://time-lime.com from Firebase to GCP.
    I've associated the domain to the Cloud Run Frontend Applicaton through GCP's custom domain solution.
    It works, but once in a while, navigating to the domain will render the old application that used to be in Firebase.
    What could be the issue?
    
    Domain Mappings in Cloud Run is giving me 4 Type A and 4 Type AAAA DNS records.
        I've only mapped on Type A and one Type AAAA to the domain in Google Domains, under Custom Records section.



            '''},
    ]
)

print(response['choices'][0]['message']['content'])