import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud import secretmanager
import json
import flask
from flask_cors import CORS
from flask import request, jsonify
from google.auth import compute_engine
import os

app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def get_creds():
    print(os.environ.get('GCP_PROJECT_NUMBER'))
    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{os.environ.get('GCP_PROJECT_NUMBER')}/secrets/GCP_CREDENTIALS/versions/latest"

        response = client.access_secret_version(name=secret_name, )
        secret = json.loads(response.payload.data.decode("UTF-8"))
    except:
        secret = 'secrets/timelime-dev-sa.json'

    cred = credentials.Certificate(secret)
    return cred

cred = get_creds()
fbapp = firebase_admin.initialize_app(cred)
db = firestore.client()

user = None

def token_required(route_function):
    def decorated_function(*args, **kwargs):
        global user

        try:
            token = request.headers.get("X-Forwarded-Authorization") if 'X-Forwarded-Authorization' in request.headers else request.headers.get("Authorization")
            decoded_token = firebase_admin.auth.verify_id_token(token.split(" ")[1])
        except Exception as e:
            print(e, flush=True)
            return jsonify({"message": 'token expired'}), 401
            if('Token expired' in str(e)):
                return jsonify({"message": 'token expired'}), 401
            else:
                return jsonify({"message": 'token error'}), 401
            
        if not token or not decoded_token:
            return jsonify({"message": "Invalid token"}), 401

        
        user = db.collection("users").where("email", "==", decoded_token['email'])

        try:
            uid = user.get()[0].id
            user = user.get()[0].to_dict()
            user['uid'] = uid
        except:
            user = None  

        return route_function(*args, **kwargs)
    
    return decorated_function

def generic_error_handler(func):
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e, flush=True)
            response = {
                'error': True,
                'message': str(e),
            }
            return jsonify(response), 500  # Return a 500 Internal Server Error
    return decorator

@app.route("/", endpoint="index")
@token_required
@generic_error_handler
def index():
    return "Hello World!"

@app.route("/auth", endpoint="get_auth")
@token_required
@generic_error_handler
def get_auth():
    if(user):
        return user
    else:
        return jsonify({"message": "User not found"})
    
@app.route("/user", methods=['POST'], endpoint="add_user")
@token_required
@generic_error_handler
def add_user():
    keys = ['email', 'displayName', 'emailVerified', 'photoURL']
    user = {key: request.json[key] for key in keys if key in request.json}
    print(user)
    db.collection("users").add(user)
    return json.dumps(user)

@app.route("/timelines", endpoint="get_timelines")
@token_required
@generic_error_handler
def get_timelines():
    print(user['uid'])
    docs = db.collection('timelines').where("uid", "==", user['uid']).order_by("lastUsed", direction=firestore.Query.DESCENDING).get()
    return json.dumps([dict(doc.to_dict(), id=doc.id) for doc in docs])

@app.route("/timeline/<timeline_id>", endpoint="get_timeline")
@token_required
@generic_error_handler
def get_timeline(timeline_id):
    doc = db.collection('timelines').document(timeline_id).get()
    doc_id = doc.id
    doc = doc.to_dict()
    doc['isEditable'] = not (user == None or doc['uid'] != user['uid'])
    doc['restrictedAccess'] = not doc['isEditable'] and not doc['isPublic']
    doc['id'] = doc_id
    return json.dumps(doc)


@app.route("/events/<timeline_id>", endpoint="get_events")
@token_required
@generic_error_handler
def get_events(timeline_id):
    docs = db.collection('events').where("tid", "==", timeline_id).get()
    return json.dumps([dict(doc.to_dict(), id=doc.id) for doc in docs])

@app.route("/categories/<timeline_id>", endpoint="get_categories")
@token_required
@generic_error_handler
def get_categories(timeline_id):
    docs = db.collection('categories').where("tid", "==", timeline_id).get()
    return json.dumps([dict(doc.to_dict(), id=doc.id) for doc in docs])

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

