# import openai
# import pandas as pd

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


import re


# Test the custom_strip method
input_str = "000-0034-007-00056"
stripped_str = input_str.lstrip("0")
print(stripped_str)  # Output: "0-0034-007-00056"