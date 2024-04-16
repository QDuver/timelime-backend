from models.db import FirestoreDB
import firebase_admin
from firebase_admin import credentials
import os
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
import json


db = None
udb = None
user = None
limiter = None

def is_prod():
    if(os.environ.get('FE_URL') == 'https://timelime.ai'):
        return True
    else:
        return False

def set_env_vars():
    if(os.environ['COMPUTERNAME'] == 'LONESSDUVERGQ'):
        os.environ['GCP_CREDENTIALS'] = 'C:/GroupM/Scripts/projects/timelime-dev-697e4c998738.json'
        with open('C:/GroupM/Scripts/projects/openai.json', 'r') as file:
            openai = json.load(file)
        os.environ['OPENAI_API_KEY'] = openai["key"]

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

