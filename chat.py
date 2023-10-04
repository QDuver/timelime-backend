import openai
from utils.utils import get_secret, set_env_variables

set_env_variables()
openai.api_key = get_secret('OpenAPI')

msg = '''
In Angular, I have three successive backend requests to trigger, and as soon as one of them is returned, I want to be able to process the response without having to wait for the others to finish.
const reqs = [this.__apiService.getTimeline('a'), this.__apiService.getTimeline('b'), this.__apiService.getTimeline('c')]
I need to be able to treat each response individually within the subscription.
What's the best rxjs operator to use in this case?
'''

response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' '''},
        {"role": "user", "content": msg},
    ]
)

print(response['choices'][0]['message']['content'])




        