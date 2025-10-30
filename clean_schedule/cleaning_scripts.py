import os
from firestore import firestore_init
from firebase_admin import firestore, auth
from config import db
firestore_init.init()


def delete_all_users():
    admin_email = os.environ.get('ADMIN_EMAIL', 'quentin.duverge@gmail.com')
    page = auth.list_users()
    for user in page.users:
        user_dict = user.__dict__['_data']
        if('email' in user_dict and user_dict['email'] == admin_email):
            continue
        else:
            auth.delete_user(user.uid)

    # Alternative using Firestore:
    # users = db.get('users')
    # for user in users:
    #     if('email' in user and user['email'] == admin_email):
    #         continue
    #     else:
    #         db.delete('users', user['id'])

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

def delete_empty_timelines():
    timelines = db.get('timelines')
    for timeline in timelines:
        events = db.get('events', where=('tid', '==', timeline['id']))
        if(len(events) == 0):
            db.delete('timelines', timeline['id'])

def delete_all_first_timelines():
    timelines = db.get('timelines')
    for timeline in timelines:
        if('name' in timeline and (timeline['name'] == 'My first timeline' or 'new timeline' in timeline['name'].lower() )):
            db.delete('timelines', timeline['id'])

def delete_all_users_timeline(userId):
    timelines = db.get('timelines', where=('uid', '==', userId))
    for timeline in timelines:
        db.delete('timelines', timeline['id'])
    events = db.get('events', where=('uid', '==', userId))
    for event in events:
        db.delete('events', event['id'])
    categories = db.get('categories', where=('uid', '==', userId))
    for category in categories:
        db.delete('categories', category['id'])

def assign_uid_to_categories():
    categories = db.get('categories')
    for category in categories:
        if('uid' not in category):
            event = db.get('event', where=('categoryId', '==', category['id']))[0]
            db.edit('categories', category['id'], {'uid': event['uid']})
