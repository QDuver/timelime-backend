from decorators.decorators import print_full_exception
import openai
from firestore.firestore_db import UnprotectedFirestoreDB, UsedDB
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
from firestore.firestore_db import db
import ai.dalle as dalle

def generate_image(type, event, timelineName = None, request=None):
    if(type == 'ai'): 
        thread = Thread(target=generate_ai_image, args=(event,))
    elif(type == 'google'): 
        thread = Thread(target=get_google_image, args=(event,))
    elif(type == 'upload'): 
        thread = Thread(target=handle_uploaded_image, args=(event, request))
    thread.start()



def _handle_async_generation(func):
    def wrapper(*args, **kwargs):
        try:
            event = args[0]
            url = func(*args, **kwargs)
            _attach_image(event, url)
            _stop_loading(event)
        except Exception as e:
            _stop_loading(event)
            print_full_exception(e)
            raise Exception('Could not generate image')    

    return wrapper

@_handle_async_generation
def generate_ai_image(event):
    prompt = _generate_prompt_from_event(event)
    url = dalle.generate_image(prompt)
    return url


@_handle_async_generation
def get_google_image(event):
    timelineName = db.get('timelines', event['tid'])['name']
    query = f"{timelineName} {event['name']}  {event['startDate'][:4]}"
    url = _fetch_google_images(query, 10)[0]
    return url

@_handle_async_generation
def handle_uploaded_image(event, request):
    bucket_name = os.environ.get('BUCKET')
    file = request.files['file']
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucket_name)
    blob = bucket.blob('images/'+event['id'])
    blob.upload_from_string( file.read(), content_type=file.content_type )
    url = f'https://storage.cloud.google.com/{bucket_name}/images/{event["id"]}'
    return url




def get_goooge_images(eventName, timelineName=None, eventStartDate= None):
    query = f"{timelineName} {eventName}  {eventStartDate[:4]}"
    links = _fetch_google_images(query, 10)
    return links

def _fetch_google_images(query, num):
    service = build("customsearch", "v1", developerKey=GOOGLE_IMAGE_API_KEY)
    result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, searchType="image", num=num).execute()
    links = [link['link'] for link in result.get("items", [])]
    db.user.update_ai_tracking_status('search', False, True)
    return links



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


def _generate_prompt_from_event(event):
    timelineName = db.get('timelines', event['tid'])['name']
    if('timeline' in timelineName.lower()):
        timelineName = ''
    prompt = f'A realistic futuristic photograph of {event["name"]}'
    if(timelineName != ''):
        prompt += f' in the context of {timelineName}'
    if("description" in event and event["description"]):
        prompt += f'. More details :  {event["description"]}'
    return prompt

def _stop_loading(event):
    event["imageGenerating"] = False
    db.edit('events', event["id"], event)
