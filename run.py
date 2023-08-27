import json
import firebase_admin
import flask
from firebase_admin import credentials
from flask_cors import CORS
from firestore_db import FirestoreDB, firestore_init
from utils import events as events
import os
from routes import timeline_bp, events_bp, auth_bp

app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.register_blueprint(timeline_bp)
app.register_blueprint(events_bp)
app.register_blueprint(auth_bp)

firestore_init.init()


app.config['db'] = FirestoreDB()
app.config['user'] = None


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)