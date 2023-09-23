from decorators.decorators import print_full_exception
import openai
from utils.utils import get_secret
import time
from flask import current_app as app

def stop_loading(event):
    db = app.config['db']
    event["imageGenerating"] = False
    db.edit('events', event["id"], event)

def generate_image(event):
    db = app.config['db']
    db.user.update_ai_tracking_status('image', True)
    try:
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
        db.user.update_ai_tracking_status('image', False, True)

        stop_loading(event)
    except Exception as e:
        stop_loading(event)
        db.user.update_ai_tracking_status('image', False, False)
        print_full_exception(e)
        raise Exception('Could not generate image')

    return event


    

    