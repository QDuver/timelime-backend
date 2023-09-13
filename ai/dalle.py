import openai
from utils.utils import get_secret
import time
from flask import current_app as app

def generate_image(event):
    print('generating image for', event["name"])
    try:
        db = app.config['db']
        prompt = f'A realistic futuristic photograph of {event["name"]}.'
        if("description" in event and event["description"]):
            prompt += f' {event["description"]}'
        openai.api_key = get_secret('OpenAPI')
        response = openai.Image.create( prompt=prompt, n=1, size='1024x1024')
        event["imageURL"] = response["data"][0]["url"]
        event["imageGenerating"] = False
        db.edit('events', event["id"], event)
    except:
        pass
    db.edit('users', db.authedUser['id'], {'generating': {'image' : {'loading': False, 'generated': event['id'] } }})
    return event


    

    