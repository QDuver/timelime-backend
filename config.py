from models.db import FirestoreDB
import firebase_admin
from firebase_admin import credentials
import os
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter


db = None
udb = None
user = None
limiter = None

def init_firebase():
    firebase_admin.initialize_app(credentials.Certificate(os.environ.get('GCP_CREDENTIALS')))

def init_db():
    global db
    db = FirestoreDB()

def init_udb():
    global udb
    udb = FirestoreDB(protected=False)

def init_limiter(app):
    global limiter
    limiter = Limiter( get_remote_address, default_limits=["10 per second"] )
    limiter.init_app(app)

def set_user(user_):
    global user
    user = user_

