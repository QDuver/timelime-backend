import openai
from utils.utils import get_secret, set_env_variables

set_env_variables()
openai.api_key = get_secret('OpenAPI')

msg = '''
In Stripe, I've been able to create a monthly subscription for a customer, with a 7 day trial.
After the 7 days, if the payment does not go through, how to catch the payment failed event? And how do I get the user's id? Can I retrieve metadata i set in the checkout session?
I use Python/Flask on server-side
'''

response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' '''},
        {"role": "user", "content": msg},
    ]
)

print(response['choices'][0]['message']['content'])




        