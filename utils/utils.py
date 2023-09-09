from google.cloud import secretmanager
import os
import json


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