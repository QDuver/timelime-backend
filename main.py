import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import secretmanager
import json
import flask
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = secretmanager.SecretManagerServiceClient()
secret_name = f"projects/82528465111/secrets/firestore_pulls/versions/latest"

response = client.access_secret_version(name=secret_name, )
secret = json.loads(response.payload.data.decode("UTF-8"))

cred = credentials.Certificate(secret)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/")
def index():
    return "Hello World!"

@app.route("/quentin")
def get_quentin():
    return "Hello Quentin!"

@app.route("/data/<collection_name>")
def get_timelines(collection_name):
    docs = db.collection(collection_name).get()
    json_data = [doc.to_dict() for doc in docs]
    return json.dumps(json_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)