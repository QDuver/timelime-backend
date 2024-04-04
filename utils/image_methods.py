from decorators.decorators import print_full_exception
import openai
from firestore.firestore_db import FirestoreDB
from models.user import User
from utils.utils import get_secret
import time
from flask import current_app as app
from google.cloud import storage
from threading import Thread
import os
from googleapiclient.discovery import build
SEARCH_ENGINE_ID = "90d862b25c6fc454e"
GOOGLE_IMAGE_API_KEY = get_secret('SEARCH_ENGINE')
from config import db

def generate_image(type, event, timelineName = None, request=None):
    _attach_image(event, True)
    if(type == 'ai'): 
        thread = Thread(target=generate_ai_image, args=(event,))
    elif(type == 'google'): 
        thread = Thread(target=get_gooogle_images, args=(event['name'], timelineName, event['startDate']))
    elif(type == 'upload'): 
        thread = Thread(target=handle_uploaded_image, args=(request, event))
    thread.start()
    return None


def generate_ai_image(event):
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

        _stop_loading(event)
    except Exception as e:
        _stop_loading(event)
        db.user.update_ai_tracking_status('image', False, False)
        print_full_exception(e)
        raise Exception('Could not generate image')
  
def get_gooogle_images(eventName, timelineName=None, eventStartDate= None, num=1):
    query = eventName + " " + eventStartDate[:4]
    service = build("customsearch", "v1", developerKey=GOOGLE_IMAGE_API_KEY)
    result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, searchType="image", num=num).execute()
    links = [link['link'] for link in result.get("items", [])]
    db.user.update_ai_tracking_status('search', False, True)
    return links

def handle_uploaded_image(request, event):
    bucket_name = os.environ.get('BUCKET')
    file = request.files['file']
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucket_name)
    blob = bucket.blob('images/'+event['id'])
    blob.upload_from_string( file.read(), content_type=file.content_type )
    event['imageName'] = event['imageURL']
    event['imageURL'] = f'https://storage.cloud.google.com/{bucket_name}/images/{event["id"]}'
    db.edit('events', event['id'], event)

def _attach_image(event, url):
    event['imageGenerating'] = True
    event['imageURL'] = url
    db.edit('events', event['id'], event)

# def handle_image(request, event):
#   
#     if('file' in request.files):
#         _handle_uploaded_image(request, event)
#     if('imageURL' in event and 'An AI image will start' in event['imageURL']):
#         event['imageGenerating'] = True
#         db.edit('events', event['id'], event)


def _stop_loading(event):
    event["imageGenerating"] = False
    db.edit('events', event["id"], event)
