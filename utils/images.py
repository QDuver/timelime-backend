from utils.decorators import print_full_exception
from google.cloud import storage
import config as c
from threading import Thread
from clients import dalle
import os
from googleapiclient.discovery import build
SEARCH_ENGINE_ID = "90d862b25c6fc454e"
GOOGLE_IMAGE_API_KEY = os.environ.get('SEARCH_ENGINE')

def generate_image(type, event, timelineName = None, request=None):
    if(type == 'ai'): 
        return generate_ai_image(event,)
    elif(type == 'google'): 
        return get_google_image(event,)
    elif(type == 'upload'): 
        return handle_uploaded_image(event, request)

def _handle_generation(func):

    def wrapper(*args, **kwargs):
        try:
            c.init_udb()
            event = args[0]
            url = func(*args, **kwargs)
            _attach_image(event, url)
            _stop_loading(event)
            return url
        except Exception as e:
            _stop_loading(event)
            print_full_exception(e)
            raise Exception('Could not generate image')    

    return wrapper

@_handle_generation
def generate_ai_image(event):
    print('Generating AI image')
    prompt = _generate_prompt_from_event(event)
    print('Prompt:', prompt)
    url = dalle.generate_image(prompt)
    print('Generated AI image', url)
    return url


@_handle_generation
def get_google_image(event):
    timelineName = c.db.get('timelines', event['tid'])['name']
    query = f"{timelineName} {event['name']}  {event['startDate'][:4]}"
    url = _fetch_google_images(query, 10)[0]
    return url

@_handle_generation
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
    return links


# def handle_image(request, event):
#   
#     if('file' in request.files):
#         _handle_uploaded_image(request, event)
#     if('imageURL' in event and 'An AI image will start' in event['imageURL']):
#         event['imageGenerating'] = True
#         db.edit('events', event['id'], event)

def _attach_image(event, url):
    event['imageGenerating'] = True
    event['imageURL'] = url
    c.udb.edit('events', event['id'], event)

def _stop_loading(event):
    event["imageGenerating"] = False
    c.udb.edit('events', event["id"], event)

def _generate_prompt_from_event(event):
    timelineName = c.udb.get('timelines', event['tid'])['name']
    if('timeline' in timelineName.lower()):
        timelineName = ''
    prompt = f'A realistic futuristic photograph of {event["name"]}'
    if(timelineName != ''):
        prompt += f' in the context of {timelineName}'
    if("description" in event and event["description"]):
        prompt += f'. More details :  {event["description"]}'
    return prompt


