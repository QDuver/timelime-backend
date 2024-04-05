import sys
from firestore.firestore_db import FirestoreDB
from models.user import User
db = None
udb = None


def init():
    global db, udb
    db = FirestoreDB()
    udb = FirestoreDB(use_limiter=False)