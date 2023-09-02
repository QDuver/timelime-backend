from google.cloud import secretmanager
import json
import firebase_admin
from firebase_admin import credentials
import os

def init():
    

    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{os.environ.get('GCP_PROJECT_NUMBER')}/secrets/GCP_CREDENTIALS/versions/latest"
        response = client.access_secret_version(name=secret_name, )
        secret = json.loads(response.payload.data.decode("UTF-8"))
    except Exception as e:
        print(e, flush=True)
        secret = 'secrets/timelime-dev-sa.json'

    cred = credentials.Certificate(secret)
    firebase_admin.initialize_app(cred)