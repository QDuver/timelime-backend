from firestore.firestore_db import FirestoreDB
db = None
udb = None
user = None


def init():
    global db, udb
    db = FirestoreDB()
    udb = FirestoreDB(use_limiter=False)