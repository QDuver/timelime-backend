import datetime
from google.cloud import secretmanager
import os
import json
from clean_schedule.main import DEFAULT_QUOTAS
from flask import jsonify, current_app as app
from google.cloud import storage
import random
from models.exceptions import CustomException
import string

def generate_random_id(length=5):
    characters = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(characters) for _ in range(length))
    return random_id

def _get_name(type_, step):
    try:
        uid = app.config['db'].user.uid
        session = app.config['session']
    except:
        uid = 'test-id'
        session = 'test-session'
    return f"{type_}/{session}-{uid}-{step}"

def _get_bucket():
    bucket_name = os.environ.get('BUCKET')
    if(not bucket_name):
        bucket_name = 'timelime-dev-bucket'
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucket_name)
    return bucket

def save_raw_to_storage(text, type_, step):
    blob = _get_bucket().blob(f'{_get_name(type_, step)}.txt')
    blob.upload_from_string(text)

def save_df_to_storage(df, type_, step):
    blob = _get_bucket().blob(f'{_get_name(type_, step)}.csv')
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')


def read_from_storage(type_):
    bucket = _get_bucket()
    blobs = bucket.list_blobs(prefix=type_)
    return sorted(blobs, key=lambda x: x.updated)
    


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
        raise CustomException(f'You can create only {DEFAULT_QUOTAS["timelines_free"]} events per timeline with the Free plan')

def timeline_quotas_exceeded():
    db = app.config['db']
    if(db.user.isPremium):
        return
    n_timelines = len(db.get('timelines', where=('uid', '==', db.uid)))
    if(n_timelines >= DEFAULT_QUOTAS['timelines_free']):
        raise CustomException(f'You can create only {DEFAULT_QUOTAS["timelines_free"]} timelines with the Free plan')


def set_env_variables():
    os.environ['GCP_PROJECT_NUMBER'] = '82528465111'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'secrets/GCP_CREDENTIALS.json'
    os.environ['FE_URL'] = 'https://localhost:4200'
    os.environ['BUCKET'] = 'timelime-dev-bucket'

def abort_if_already_ai_generating():
    db = app.config['db']
    user = db.user
    try:
        if(user.generating['quiz']['loading'] or user.generating['timeline']['loading']):
            return jsonify({"message": "You already have a quiz or timeline being generated"}), 400
    except KeyError:
        pass