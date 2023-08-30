

from firestore.firestore_db import FirestoreDB, UnprotectedFirestoreDB
from firebase_admin import firestore

db = UnprotectedFirestoreDB()

def delete_timeline(timeline_id):
    db.delete('timelines', timeline_id)
    events = db.get('events', where=('tid', '==', timeline_id))
    for event in events:
        db.delete('events', event['id'])


def delete_all(collection):

    db = firestore.client()
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

def delete_all_orphan_events():
    events = db.get('events')
    timelines = db.get('timelines')
    tids = [timeline['id'] for timeline in timelines]
    for event in events:
        if('tid' in event and event['tid'] not in tids):
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
