import json
import firebase_admin
import flask
from firebase_admin import credentials
from flask_cors import CORS
from firestore_db import FirestoreDB
from utils import events as events
from google.cloud import secretmanager
import os
from routes import timeline_bp, events_bp, auth_bp

app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.register_blueprint(timeline_bp)
app.register_blueprint(events_bp)
app.register_blueprint(auth_bp)
try:
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{os.environ.get('GCP_PROJECT_NUMBER')}/secrets/GCP_CREDENTIALS/versions/latest"
    response = client.access_secret_version(name=secret_name, )
    secret = json.loads(response.payload.data.decode("UTF-8"))
except:
    secret = 'secrets/timelime-dev-sa.json'

cred = credentials.Certificate(secret)
firebase_admin.initialize_app(cred)

app.config['db'] = FirestoreDB()
app.config['user'] = None


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)