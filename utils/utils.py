from google.cloud import secretmanager
import os
import json
from flask import jsonify, current_app as app
import logging

logger = logging.getLogger('my_logger')
logger.setLevel(logging.WARNING)

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


def set_env_variables():
    os.environ['GCP_PROJECT_NUMBER'] = '82528465111'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'secrets/GCP_CREDENTIALS.json'

def print_full_exception(e):
    logger.error('This is an warning message')
    logger.error(e.__traceback__.tb_frame.f_code.co_filename)
    logger.error(e.__traceback__.tb_lineno)
    print("An exception occurred:", e)
    print("File:", e.__traceback__.tb_frame.f_code.co_filename)
    print("Line:", e.__traceback__.tb_lineno)


def abort_if_already_ai_generating():
    db = app.config['db']
    user = db.authedUser
    try:
        if(user['generating']['quiz']['loading'] or user['generating']['timeline']['loading']):
            return jsonify({"message": "You already have a quiz or timeline being generated"}), 400
    except KeyError:
        pass