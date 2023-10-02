import openai
from utils.utils import get_secret, set_env_variables

set_env_variables()
openai.api_key = get_secret('OpenAPI')

msg = '''
I have this in my Angular SSR code but I don't remember why it's there :
RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules, initialNavigation: 'enabledBlocking', useHash: true})
It's in app-routing.module.ts.
It's adding a "#" after the root url.
Is there a reason for this, and is there a way to remove it?
'''

response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' '''},
        {"role": "user", "content": msg},
    ]
)

print(response['choices'][0]['message']['content'])




        