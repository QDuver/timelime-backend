import json
import firebase_admin
import flask
from firebase_admin import firestore, auth, credentials
from flask import jsonify, request
from flask_cors import CORS
from firestore_db import FirestoreDB
import events
from google.cloud import secretmanager
import os
import time
import datetime

app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
user = None
try:
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{os.environ.get('GCP_PROJECT_NUMBER')}/secrets/GCP_CREDENTIALS/versions/latest"
    response = client.access_secret_version(name=secret_name, )
    secret = json.loads(response.payload.data.decode("UTF-8"))
except:
    secret = 'secrets/timelime-dev-sa.json'

cred = credentials.Certificate(secret)
firebase_admin.initialize_app(cred)
db = FirestoreDB()

def token_required(route_function):
    def decorated_function(*args, **kwargs):
        global user
        global db

        try:
            token = request.headers.get("X-Forwarded-Authorization") if 'X-Forwarded-Authorization' in request.headers else request.headers.get("Authorization")
            decoded_token = firebase_admin.auth.verify_id_token(token.split(" ")[1])
        except Exception as e:
            print(e, flush=True)
            if('Token expired' in str(e)):
                return jsonify({"message": 'Token expired'}), 401
            else:
                return jsonify({"message": 'Unauthorized'}), 401
            
        if not token or not decoded_token:
            return jsonify({"message": "Invalid token"}), 401

        try:
            user = db.get("users", where=('email', '==', decoded_token['email']))[0]
            db.set_user(user)
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


@app.route("/auth", endpoint="get_auth")
@token_required
# @generic_error_handler
def get_auth():
    if(user):
        return user
    else:
        return jsonify({"message": "User not found"})
    
@app.route("/user", methods=['POST'], endpoint="add_user")
@token_required
# @generic_error_handler
def add_user():
    print('add_user', request.json, flush=True)
    existing_user = db.get("users", where=('email', '==', request.json['email']))
    if(len(existing_user) > 0):
        return json.dumps(existing_user[0])


    keys = ['email', 'displayName', 'photoURL', 'uid']
    user = {key: request.json[key] for key in keys if key in request.json}
    db.add("users", user, doc_id=request.json['uid'])
    return json.dumps(user)

@app.route("/user", methods=['PUT'], endpoint="edit_user")
@token_required
# @generic_error_handler
def edit_user():
    user = request.json
    db.edit("users", user['uid'], user)
    return json.dumps(user)

@app.route("/timelines", endpoint="get_timelines")
@token_required
# @generic_error_handler
def get_timelines():
    timelines = db.get("timelines", where=('uid', '==', user['uid']), order_by=('lastUsed', 'DESCENDING'))
    return json.dumps(timelines)

@app.route("/timeline/<timeline_id>", endpoint="get_timeline")
@generic_error_handler
def get_timeline(timeline_id):
    doc = db.get("timelines", doc=timeline_id)
    doc['lastUsed'] = int(time.time())
    try:
        db.edit("timelines", timeline_id, doc)
    except: 
        pass

    if(db.authedUser['uid'] != doc['uid']):
        if(not doc['isPublic']):
            return jsonify({"message": "This timeline can only be viewed by its owner"}), 401
        else:
            doc['isEditable'] = False
    return json.dumps(doc)


@app.route("/timeline", endpoint="edit_timeline", methods=['PUT'])
@token_required
@generic_error_handler
def edit_timeline():
    timeline = request.json
    db.edit("timelines", timeline['id'], timeline)
    return json.dumps(timeline)

@app.route("/timeline", endpoint="create_timeline", methods=['POST'])
@token_required
@generic_error_handler
def create_timeline():
    timeline = {'uid': user['uid'], 'name': 'New timeline', 'isPublic': False, 'lastUsed': int(time.time())}
    timeline['id'] = db.add("timelines", timeline)
    default_event = {'uid': user['uid'], 'tid': timeline['id'], 'name': 'New event', 'startDate': datetime.datetime.now().strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    events.create_or_edit_event(default_event, db)
    return json.dumps(timeline)

@app.route("/timeline/<timeline_id>", endpoint="delete_timeline", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_timeline(timeline_id):
    db.delete("timelines", timeline_id)
    return json.dumps({})

@app.route("/events/<timeline_id>", endpoint="get_events")
@token_required
# @generic_error_handler
def get_events(timeline_id):
    ev = events.get_events(timeline_id, db)
    return json.dumps(ev)

@app.route("/events", endpoint="post_event", methods=['POST'])
@token_required
@generic_error_handler
def post_event():
    event = request.json
    events.create_or_edit_event(event, db)
    return json.dumps(event)


@app.route("/event/<event_id>", endpoint="delete_event", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_event(event_id):
    db.delete("events", event_id)
    return json.dumps({})


@app.route("/categories/<timeline_id>", endpoint="get_categories", methods=['GET'])
@token_required
@generic_error_handler
def get_categories(timeline_id):
    categories = db.get("categories", where=('tid', '==', timeline_id))
    return json.dumps(categories)

@app.route("/categories/<catgory_id>", endpoint="delete_category", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_category(catgory_id):
    db.delete("categories", catgory_id)
    events = db.get("events", where=('category', '==', catgory_id))
    for event in events:
        event['categoryId'] = None
        events.create_or_edit_event(event)

    return json.dumps({})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
