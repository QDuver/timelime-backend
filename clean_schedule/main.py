import time
from google.cloud import secretmanager
import json
import firebase_admin
from firebase_admin import credentials, firestore
import os

DEFAULT_QUOTAS = {
    'search': 300,
    'quiz': 200,
    'timeline': 200,
    'timelines_free': 5,
    'events_free': 30,
    'image': 50,
    'premium': 4
}

# gcloud functions deploy clean-schedule --runtime python38 --project timelime-prod --entry-point clean_schedule --region europe-west2 --source clean_schedule --trigger-http --set-env-vars GCP_PROJECT_NUMBER=260031091728
# gcloud scheduler jobs create http clean-schedule --project timelime-prod --schedule "0 4,16 * * *" --uri=https://europe-west2-timelime-prod.cloudfunctions.net/clean-schedule --location europe-west2

class UnprotectedFirestoreDB:

    def __init__(self):
        self.db = firestore.client()

    def delete(self, collection, doc):
        return self.db.collection(collection).document(doc).delete()
    
    def get(self, collection, doc=None, where=None, order_by=None, limit=None):
        data = self.db.collection(collection)
        if doc:
            data = data.document(doc)
        if where:
            data = data.where(*where)
        if order_by:
            data = data.order_by(*order_by)

        try:
            if not doc:
                return [dict(doc.to_dict(), id=doc.id) for doc in data.get()]
            if(doc):
                return dict(data.get().to_dict(), id=doc)
        except Exception as e:
            return None


def clean_schedule(request):

    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{os.environ.get('GCP_PROJECT_NUMBER')}/secrets/GCP_CREDENTIALS/versions/latest"
    response = client.access_secret_version(name=secret_name, )
    secret = json.loads(response.payload.data.decode("UTF-8"))

    cred = credentials.Certificate(secret)
    firebase_admin.initialize_app(cred)
    print(DEFAULT_QUOTAS, flush=True)

    db = UnprotectedFirestoreDB()
    timelines = db.get('timelines')
    anonymous_timelines = [timeline for timeline in timelines if len(timeline['uid']) < 12]
    unique_tids = list(set([timeline['id'] for timeline in anonymous_timelines]))

    events = db.get('events')
    for event in events:
        if(event['tid'] in unique_tids):
            db.delete('events', event['id'])

    for category in db.get('categories'):
        if(category['tid'] in unique_tids):
            db.delete('categories', category['id'])

    for user in db.get('users'):
        if('isAnonymous' in user and user['isAnonymous'] and time.time() - user['joinedOn'] > 500):
            db.delete('users', user['uid'])

    for timeline in anonymous_timelines:
        db.delete('timelines', timeline['id'])

    # Refresh quotas each end of month
    if(time.localtime().tm_mday == 1):
        for user in db.get('users'):
            db.edit('users', user['uid'], {'quotas': DEFAULT_QUOTAS})

    return 'ok'