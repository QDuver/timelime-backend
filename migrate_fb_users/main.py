import firebase_admin
from firebase_admin import auth, credentials, firestore


def migrate_to_firestore():

    secret = './secrets/timelime-dev-sa.json'
    cred = credentials.Certificate(secret)
    firebase_admin.initialize_app(cred)
    page = auth.list_users()
    db = firestore.client()
    while page:
        for user in page.users:
            data = user.__dict__['_data']
            user2 = {'uid': data['localId']}
            if('email' in data):
                user2['email'] = data['email']
            if('emailVerified' in data):
                user2['emailVerified'] = data['emailVerified']
            if('displayName' in data):
                user2['displayName'] = data['displayName']
            if('photoUrl' in data):
                user2['photoUrl'] = data['photoUrl']

            # print(user2)
            db.collection('users').document(data['localId']).set(user2)
            # users.append(user)
        page = page.get_next_page()



def init_source(name):
    secret = './secrets/timelime-dev-sa.json'
    cred = credentials.Certificate(secret)
    firebase_admin.initialize_app(cred)
    page = auth.list_users()
    while page:
        for user in page.users:
            print(user.__dict__, flush=True)
            # users.append(user)
        page = page.get_next_page()

def init_destination(name):
    secret = 'migrate_fb_users/secrets/destination.json'
    cred = credentials.Certificate(secret)
    destination = firebase_admin.initialize_app(cred, name=name)
    # destination_auth = auth.get_auth(destination)
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

migrate_to_firestore()
# init_destination('destination')


