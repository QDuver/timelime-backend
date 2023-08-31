import firebase_admin
from firebase_admin import auth, credentials, firestore
import os

users = []

def init_source():
    secret = 'migrations/secrets/prod.json'
    cred = credentials.Certificate(secret)
    firebase_admin.initialize_app(cred)
    page = auth.list_users()
    while page:
        for user in page.users:
            users.append(user)
            try:
                print(user.__dict__['_data'])
            except:
                pass
        page = page.get_next_page()

def init_destination(name):
    secret = 'migrations/secrets/prod.json'
    cred = credentials.Certificate(secret)
    destination = firebase_admin.initialize_app(cred, name=name)
    for user in users:
        try:
            auth.create_user(
                uid=user.uid,
                email=user.email,
                display_name=user.display_name,
                photo_url=user.photo_url,
                email_verified=user.email_verified,
                app=destination
        )
        except Exception as e:
            print(e)
            pass

init_source()
# init_destination('destination')


