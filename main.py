import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import secretmanager
import json

def get_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    try:
        response = client.access_secret_version(name=secret_name, )
        return json.loads(response.payload.data.decode("UTF-8"))
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None

# Replace 'your_project_id' and 'your_secret_id' with your actual GCP project ID and secret ID.
project_id = "82528465111"
secret_id = "firestore_pulls"


secret = get_secret(project_id, secret_id)
cred = credentials.Certificate(secret)

firebase_admin.initialize_app(cred)

db = firestore.client()
collection = db.collection("timelines")

docs = collection.get()

for doc in docs:
    print(doc.to_dict())