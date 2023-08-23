import firebase_admin
from firebase_admin import auth, credentials

users = []


def init_source(name):
    secret = 'migrate_fb_users/secrets/source.json'
    cred = credentials.Certificate(secret)
    firebase_admin.initialize_app(cred)
    page = auth.list_users()
    while page:
        for user in page.users:
            print(user)
            users.append(user)
        page = page.get_next_page()

def init_destination(name):
    secret = 'migrate_fb_users/secrets/destination.json'
    cred = credentials.Certificate(secret)
    destination = firebase_admin.initialize_app(cred, name=name)
    # destination_auth = auth.get_auth(destination)
    for user in users:
        print(user)
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

init_source('source')
init_destination('destination')


