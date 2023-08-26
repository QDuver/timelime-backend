import json
import firebase_admin
from firebase_admin import firestore, auth, credentials
from firestore_db import FirestoreDB
from google.cloud import secretmanager
import os

try:
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{os.environ.get('GCP_PROJECT_NUMBER')}/secrets/GCP_CREDENTIALS/versions/latest"
    response = client.access_secret_version(name=secret_name, )
    secret = json.loads(response.payload.data.decode("UTF-8"))
except:
    secret = 'secrets/timelime-dev-sa.json'

cred = credentials.Certificate(secret)
firebase_admin.initialize_app(cred)
# db = FirestoreDB()
db = firestore.client()

def delete_all(collection):

    docs = db.collection(collection)
    for doc in docs.stream():
        doc.reference.delete()


def delete_all_my_first_event_events():
    events = db.get('events')
    for event in events:
        if('name' in event and event['name'] == 'My first event'):
            db.delete('events', event['id'])

def delete_all_events_without_uid():
    events = db.get('events')
    for event in events:
        if('uid' not in event):
            db.delete('events', event['id'])

def delete_all_first_timelines():
    timelines = db.get('timelines')
    for timeline in timelines:
        if('name' in timeline and (timeline['name'] == 'My first timeline' or timeline['name'] == 'New timeline' )):
            db.delete('timelines', timeline['id'])

def assign_uid_to_categories():
    categories = db.get('categories')
    for category in categories:
        if('uid' not in category):
            event = db.get('event', where=('categoryId', '==', category['id']))[0]
            db.edit('categories', category['id'], {'uid': event['uid']})

if __name__ == "__main__":
    delete_all('users')