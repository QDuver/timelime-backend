from firebase_admin import firestore
from utils.constants import DEFAULT_QUOTAS
from functools import wraps
import config as c

class FirestoreDB: 

    def __init__(self, protected=True):
        
        self.protected = protected
        self.db = firestore.client()
        self._set_limits(protected)


    # def forbid_if_too_many_entries(self, collection):
    #     if(collection == 'timelines' and len(self.get('timelines', where=('uid', '==', self.uid))) > 100):
    #         raise Exception("You've reached the maximum quota of timelines")

    #     if(collection == 'categories' and len(self.get('categories', where=('uid', '==', self.uid))) > 1000):
    #         raise Exception("You've reached the maximum quota of categories")
        
    #     if(collection == 'events' and len(self.get('events', where=('uid', '==', self.uid))) > 1000):
    #         raise Exception("You've reached the maximum quota of events")

    def delete(self, collection, doc):
        self._forbid_if_not_owner(collection, doc)
        return self.db.collection(collection).document(doc).delete()
    
    def edit(self, collection, doc, data):
        self._forbid_if_not_owner(collection, doc)
        return self.db.collection(collection).document(doc).update(data)

    def add(self, collection, data, doc_id=None):
        if(doc_id):
            return self.db.collection(collection).document(doc_id).set(data)
        else:
            return self.db.collection(collection).add(data)[1].id
        
    def add_batch(self, collection, data):
        batch = self.db.batch()
        ids = []
        for doc in data:
            ref = self.db.collection(collection).document()
            ids.append(ref.id)
            batch.set(ref, doc)
        batch.commit()
        return ids

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


    def _set_limits(self, protected):
        if(protected):
            self.delete = self._apply_limit(self.delete, "30/minute")
            self.edit = self._apply_limit(self.edit, "30/minute")
            self.add = self._apply_limit(self.add, "40/minute")
            self.add_batch = self._apply_limit(self.add_batch, "5/minute")
            self.get = self._apply_limit(self.get, "20/second")

    def _apply_limit(self, func, rate):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return c.limiter.limit(rate)(wrapper)

    def _forbid_if_not_owner(self, collection, doc):
        if not (self.protected):
            return
        doc = self.db.collection(collection).document(doc).get().to_dict()
        if(c.user.uid != doc['uid']):
            raise Exception('You are not the owner of this timeline')