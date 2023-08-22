from firebase_admin import firestore


class FirestoreDB: 

    def __init__(self):
        self.db = firestore.client()

    def delete(self, collection, doc):
        return self.db.collection(collection).document(doc).delete()
    
    def edit(self, collection, doc, data):
        return self.db.collection(collection).document(doc).update(data)

    def add(self, collection, data):
        return self.db.collection(collection).add(data)[1].id

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
