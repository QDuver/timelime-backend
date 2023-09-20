import datetime
from google.cloud import secretmanager
import os
import json
from flask import jsonify, current_app as app
import logging
import traceback

logger = logging.getLogger('my_logger')
logger.setLevel(logging.WARNING)
from google.cloud import storage

def save_text_to_storage(text, name):
    bucket_name = os.environ.get('BUCKET')
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucket_name)
    blob = bucket.blob(f'{name}.txt')
    blob.upload_from_string(text)

def save_df_to_storage(df, name):
    bucket_name = os.environ.get('BUCKET')
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucket_name)
    blob = bucket.blob(f'{name}.csv')
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')

def read_from_storage(name):
    bucket_name = os.environ.get('BUCKET')
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucket_name)
    blob = bucket.blob(f'{name}.csv')
    blob.download_to_filename(f'{name}.csv')

def get_fe_url():
    try:
        return os.environ.get('FE_URL')
    except:
        set_env_variables()
        return os.environ.get('FE_URL')

def get_secret(secret_name):
    try:
        return get_secret_core(secret_name)
    except:
        set_env_variables()
        return get_secret_core(secret_name)

def get_secret_core(secret_name):

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


def set_env_variables():
    os.environ['GCP_PROJECT_NUMBER'] = '82528465111'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'secrets/GCP_CREDENTIALS.json'
    os.environ['FE_URL'] = 'https://localhost:4200'

def print_full_exception(e):
    logger.error('This is an warning message')
    logger.error(traceback.print_tb(e.__traceback__))
    # logger.error(e.__traceback__.tb_lineno)


def abort_if_already_ai_generating():
    db = app.config['db']
    user = db.user
    try:
        if(user.generating['quiz']['loading'] or user.generating['timeline']['loading']):
            return jsonify({"message": "You already have a quiz or timeline being generated"}), 400
    except KeyError:
        pass