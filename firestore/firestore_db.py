from firebase_admin import firestore
from decorators.decorators import limiter
from flask import current_app as app
class FirestoreDB: 

    uid = None
    def __init__(self):
        self.db = firestore.client()

    def forbid_if_too_many_entries(self, collection):
        if(collection == 'timelines' and len(self.get('timelines', where=('uid', '==', self.uid))) > 100):
            raise Exception("You've reached the maximum quota of timelines")

        if(collection == 'categories' and len(self.get('categories', where=('uid', '==', self.uid))) > 1000):
            raise Exception("You've reached the maximum quota of categories")
        
        if(collection == 'events' and len(self.get('events', where=('uid', '==', self.uid))) > 1000):
            raise Exception("You've reached the maximum quota of events")

    def forbid_if_not_owner(self, collection, doc):
        doc = self.db.collection(collection).document(doc).get().to_dict()
        if(self.uid == 'BaxP33wjGCV5iUTKxiPs5b0Bx4c2'):
            return
        if(doc['uid'] != self.uid):
            raise Exception('You are not the owner of this timeline')

    def delete(self, collection, doc):
        self.forbid_if_not_owner(collection, doc)
        return self.db.collection(collection).document(doc).delete()
    
    @limiter.limit("30/minute")
    def edit(self, collection, doc, data):
        self.forbid_if_not_owner(collection, doc)
        return self.db.collection(collection).document(doc).update(data)

    @limiter.limit("20/minute")
    def add(self, collection, data, doc_id=None):
        self.forbid_if_too_many_entries(collection)
        if(doc_id):
            return self.db.collection(collection).document(doc_id).set(data)
        else:
            return self.db.collection(collection).add(data)[1].id
        
    @limiter.limit("5/minute")
    def add_batch(self, collection, data):
        batch = self.db.batch()
        for doc in data:
            ref = self.db.collection(collection).document()
            batch.set(ref, doc)
        return batch.commit()

    @limiter.limit("10/second")
    def get(self, collection, doc=None, where=None, order_by=None, limit=None):
        data = self.db.collection(collection)
        if doc:
            data = data.document(doc)
        if where:
            data = data.where(*where)
        if order_by:
            data = data.order_by(*order_by)

        if not doc:
            return [dict(doc.to_dict(), id=doc.id) for doc in data.get()]
        if(doc):
            return dict(data.get().to_dict(), id=doc)


class UnprotectedFirestoreDB:

    uid = None
    def __init__(self):
        self.db = firestore.client()

    def delete(self, collection, doc):
        return self.db.collection(collection).document(doc).delete()
    
    def edit(self, collection, doc, data):
        return self.db.collection(collection).document(doc).update(data)

    def add(self, collection, data, doc_id=None):
        if(doc_id):
            return self.db.collection(collection).document(doc_id).set(data)
        else:
            return self.db.collection(collection).add(data)[1].id

    def add_batch(self, collection, data):
        batch = self.db.batch()
        for doc in data:
            ref = self.db.collection(collection).document()
            batch.set(ref, doc)
        return batch.commit()

    def get(self, collection, doc=None, where=None, order_by=None, limit=None):
        data = self.db.collection(collection)
        if doc:
            data = data.document(doc)
        if where:
            data = data.where(*where)
        if order_by:
            data = data.order_by(*order_by)

        try:
            if not doc:
                return [dict(doc.to_dict(), id=doc.id) for doc in data.get()]
            if(doc):
                return dict(data.get().to_dict(), id=doc)
        except Exception as e:
            return None
