import datetime
from google.cloud import secretmanager
import os
import json
from flask import jsonify, current_app as app
from google.cloud import storage
import random
from models.exceptions import CustomException
import string

from utils.constants import DEFAULT_QUOTAS

def divide_chunks(l, n): 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def generate_random_id(length=5):
    characters = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(characters) for _ in range(length))
    return random_id

def get_secret(secret_name):

    if(secret_name == 'GCP_CREDENTIALS' and os.environ.get('FE_URL') == 'https://localhost:4200'):
        return json.load(open('secrets/GCP_CREDENTIALS.json'))

    client = secretmanager.SecretManagerServiceClient()
    secret = f"projects/{os.environ.get('GCP_PROJECT_NUMBER')}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=secret, )
    try:
        return json.loads(response.payload.data.decode("UTF-8"))
    except:
        return response.payload.data.decode("UTF-8")

def first_day_of_next_month():

    current_date = datetime.date.today()

    next_month = current_date.month + 1 if current_date.month < 12 else 1
    next_year = current_date.year + 1 if current_date.month == 12 else current_date.year
    first_day_of_next_month = datetime.date(next_year, next_month, 1)

    timestamp = datetime.datetime.combine(first_day_of_next_month, datetime.time()).timestamp()
    return timestamp

def event_quotas_exceeded(event):
    db = app.config['db']
    if(db.user.isPremium):
        return False
    n_events = len(db.get('events', where=('tid', '==', event['tid'])))
    if(n_events >= DEFAULT_QUOTAS['events_free']):
        raise CustomException(f'backend.freeEventsQuotaReached')

def timeline_quotas_exceeded():
    db = app.config['db']
    if(db.user.isPremium):
        return
    n_timelines = len(db.get('timelines', where=('uid', '==', db.uid)))
    if(n_timelines >= DEFAULT_QUOTAS['timelines_free']):
        raise CustomException(f'backend.freeTimelinesQuotaReached.{DEFAULT_QUOTAS["timelines_free"]}')


def set_env_variables():
    os.environ['GCP_PROJECT_NUMBER'] = '82528465111'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'secrets/GCP_CREDENTIALS.json'
    os.environ['FE_URL'] = 'https://localhost:4200'
    os.environ['BUCKET'] = 'timelime-dev-bucket'
    os.environ['OPENAI_API_KEY'] = get_secret('OpenAPI')

def abort_if_already_ai_generating():
    db = app.config['db']
    user = db.user
    try:
        if(user.generating['quiz']['loading'] or user.generating['timeline']['loading']):
            return jsonify({"message": "loadingTracker.quizOrTimelineAlreadyGenerating"}), 400
    except KeyError:
        pass