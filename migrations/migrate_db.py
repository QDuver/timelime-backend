import firebase_admin
from firebase_admin import auth, credentials, firestore
import os

def init_projects():
    source_cred = credentials.Certificate('migrations/secrets/pre-prod.json')
    source_app = firebase_admin.initialize_app(source_cred)
    source_db = firestore.client()

    target_cred = credentials.Certificate('migrations/secrets/prod.json')
    target_app = firebase_admin.initialize_app(target_cred, name='target')
    target_db = firestore.client(app=target_app)
    return source_db, target_db

def migrate_users(source_db, target_db):
    page = auth.list_users()
    while page:
        for user in page.users:
            data = user.__dict__['_data']
            user2 = {'uid': data['localId']}
            if('email' in data):
                user2['email'] = data['email']
            if('displayName' in data):
                user2['displayName'] = data['displayName']
            if('photoUrl' in data):
                user2['photoUrl'] = data['photoUrl']

            target_db.collection('users').document(data['localId']).set(user2)
        page = page.get_next_page()





def migrate_categories(source_db, target_db):
    cats = source_db.collection('categories').get()
    for cat in cats:
        cat_dict = cat.to_dict()
        print(cat_dict)
        if('user' in cat_dict):
            cat_dict['uid'] = cat_dict['user']
            del cat_dict['user']
        print(cat_dict)
        target_db.collection('categories').document(cat.id).set(cat_dict)

def migrate_timelines(source_db, target_db):
    timelines = source_db.collection('timelines').get()
    for timeline in timelines:
        timeline_dict = timeline.to_dict()
        print(timeline_dict)
        if('uid' not in timeline_dict):
            raise Exception('Timeline has no uid')
        print(timeline_dict)
        # target_db.collection('timelines').document(timeline.id).set(timeline_dict)


def migrate_example_timelines(source_db, target_db):
    source_events = source_db.collection('events').where('tid', '==', 'bAIsSOGstg4ySzHAKV59').get()
    source_categories = source_db.collection('categories').where('tid', '==', 'bAIsSOGstg4ySzHAKV59').get()
    source_timeline = source_db.collection('timelines').document('bAIsSOGstg4ySzHAKV59').get()
    for event in source_events:
        target_db.collection('events').document(event.id).set(event.to_dict())
    for category in source_categories:
        target_db.collection('categories').document(category.id).set(category.to_dict())
    target_db.collection('timelines').document('bAIsSOGstg4ySzHAKV59').set(source_timeline.to_dict())


source_db, target_db = init_projects()
migrate_example_timelines(source_db, target_db)