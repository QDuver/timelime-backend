import firebase_admin
from firebase_admin import credentials

from utils.utils import get_secret

def init():
    secret = get_secret('GCP_CREDENTIALS')
    cred = credentials.Certificate(secret)
    firebase_admin.initialize_app(cred)