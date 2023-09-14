import openai
from utils.utils import get_secret, print_full_exception
import time
from flask import current_app as app

def generate_image(event):
    try:
        db = app.config['db']
        timelineName = db.get('timelines', event['tid'])['name']
        if('timeline' in timelineName.lower()):
            timelineName = ''
        prompt = f'A realistic futuristic photograph of {event["name"]}'
        if(timelineName != ''):
            prompt += f' in the context of {timelineName}'
        if("description" in event and event["description"]):
            prompt += f'. More details :  {event["description"]}'
        openai.api_key = get_secret('OpenAPI')
        response = openai.Image.create( prompt=prompt, n=1, size='1024x1024')
        event["imageURL"] = response["data"][0]["url"]
        event["imageGenerating"] = False
        db.edit('events', event["id"], event)
    except Exception as e:
        event['imageGenerating'] = False
        db.edit('events', event["id"], event)
        db.edit('users', db.authedUser['id'], {'generating': {'image' : {'loading': False, 'generated': event['id'] } }})
        print_full_exception(e)
        raise Exception('Could not generate image')

    return event


    

    