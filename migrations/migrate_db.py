import firebase_admin
from firebase_admin import auth, credentials, firestore
import os

from utils.utils import set_env_variables

def init_projects():
    preprod_cred = credentials.Certificate('secrets/GCP_CREDENTIALS.json')
    preprod_app = firebase_admin.initialize_app(preprod_cred)
    preprod_db = firestore.client()

    prod_cred = credentials.Certificate('secrets/GCP_CREDENTIALS_PROD.json')
    prod_app = firebase_admin.initialize_app(prod_cred, name='target')
    prod_db = firestore.client(app=prod_app)
    return preprod_db, prod_db

def migrate_users(preprod_db, prod_db):
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

            prod_db.collection('users').document(data['localId']).set(user2)
        page = page.get_next_page()





def migrate_categories(preprod_db, prod_db):
    cats = preprod_db.collection('categories').get()
    for cat in cats:
        cat_dict = cat.to_dict()
        if('user' in cat_dict):
            cat_dict['uid'] = cat_dict['user']
            del cat_dict['user']
        prod_db.collection('categories').document(cat.id).set(cat_dict)

def migrate_timelines(preprod_db, prod_db):
    timelines = preprod_db.collection('timelines').get()
    for timeline in timelines:
        timeline_dict = timeline.to_dict()
        if('uid' not in timeline_dict):
            raise Exception('Timeline has no uid')
        # prod_db.collection('timelines').document(timeline.id).set(timeline_dict)


def migrate_example_timelines(preprod_db, prod_db, timeline_id):
    preprod_events = preprod_db.collection('events').where('tid', '==', timeline_id).get()
    preprod_categories = preprod_db.collection('categories').where('tid', '==', timeline_id).get()
    preprod_timeline = preprod_db.collection('timelines').document(timeline_id).get()
    for event in preprod_events:
        prod_db.collection('events').document(event.id).set(event.to_dict())
    for category in preprod_categories:
        prod_db.collection('categories').document(category.id).set(category.to_dict())
    prod_db.collection('timelines').document(timeline_id).set(preprod_timeline.to_dict())

def migrate_example_quizzes(tids):
    preprod_db, prod_db = init_projects()
    for tid in tids:
        quiz = preprod_db.collection('quizzes').where('tid', '==', tid).get()[0]
        prod_db.collection('quizzes').document(quiz.id).set(quiz.to_dict())
        prod_db.collection('quizzes').document(quiz.id).update({'uid': 'ZhPpeqGHXVRZ73ohiwzhYtFFZ7O2'})


def change_timeline_uid(db, old, new):
    events = db.collection('events').where('uid', '==', old).get() 
    categories = db.collection('categories').where('uid', '==', old).get()
    timelines = db.collection('timelines').where('uid', '==', old).get()
    quizzes = db.collection('quizzes').where('uid', '==', old).get()
    for event in events:
        db.collection('events').document(event.id).update({'uid': new})
    for category in categories:
        db.collection('categories').document(category.id).update({'uid': new})
    for timeline in timelines:
        db.collection('timelines').document(timeline.id).update({'uid': new})
    for quiz in quizzes:
        db.collection('quizzes').document(quiz.id).update({'uid': new})
    

def modify_example_timelines(preprod_db, prod_db):
    db = prod_db
    timelines = db.collection('timelines').where('uid', '==', '0Gu3S71O2Thq0bSv5DTY7pszf1P2').get()
    for timeline in timelines:
        db.collection('timelines').document(timeline.id).update({'uid': 'ZhPpeqGHXVRZ73ohiwzhYtFFZ7O2'})
        db.collection('timelines').document(timeline.id).update({'isPublic': True})