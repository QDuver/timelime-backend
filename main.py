import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

print('coucou')

# Create a service account and initialize the Firestore client.
cred = credentials.Certificate("firestore_pulls.json")
firebase_admin.initialize_app(cred)

# Create a reference to the collection you want to read data from.
db = firestore.client()
collection = db.collection("categories")

# Get all the documents in the collection.
docs = collection.get()

# Iterate over the documents and print their data.
for doc in docs:
    print(doc.to_dict())
