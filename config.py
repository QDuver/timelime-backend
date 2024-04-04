from firestore.firestore_db import FirestoreDB
db = None


def init():
    global db
    db = FirestoreDB()