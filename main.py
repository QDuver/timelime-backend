import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud import secretmanager
import json
import flask
from flask_cors import CORS
from flask import request, jsonify

app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# client = secretmanager.SecretManagerServiceClient()
# secret_name = f"projects/82528465111/secrets/firestore_pulls/versions/latest"

# response = client.access_secret_version(name=secret_name, )
# secret = json.loads(response.payload.data.decode("UTF-8"))

secret = 'secrets/timelime-dev-7f677154d05e.json'

cred = credentials.Certificate(secret)
fbapp = firebase_admin.initialize_app(cred)
db = firestore.client()

user = None

def token_required(route_function):
    def decorated_function(*args, **kwargs):
        global user
        print(request)
        try:
            token = request.headers.get("Authorization")
            decoded_token = firebase_admin.auth.verify_id_token(token.split(" ")[1])
        except Exception as e:
            print(e, flush=True)
            return jsonify({"message": 'token error'}), 401
            
        if not token or not decoded_token:
            return jsonify({"message": "Invalid token"}), 401

        
        user = db.collection("users").where("email", "==", decoded_token['email']).limit(1)

        try:
            user = user.get()[0].to_dict()   
        except:
            return jsonify({"message": "Invalid user"}), 401   

        return route_function(*args, **kwargs)
    
    return decorated_function

@app.route("/", endpoint="index")
@token_required
def index():
    print(user, flush=True)
    return "Hello World!"

@app.route("/quentin", endpoint="get_quentin")
@token_required
def get_quentin():
    return "Hello Quentin!"

@app.route("/data/<collection_name>", endpoint="get_timelines")
@token_required
def get_timelines(collection_name):
    docs = db.collection(collection_name).get()
    json_data = [doc.to_dict() for doc in docs]
    return json.dumps(json_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

