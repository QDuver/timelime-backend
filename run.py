import flask
from flask_cors import CORS
from firestore.firestore_db import FirestoreDB
import firestore.firestore_init as firestore_init
from utils import methods as methods
from routes import timeline_bp, events_bp, auth_bp, other_bp
from decorators.decorators import limiter


app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
limiter.init_app(app)

app.register_blueprint(timeline_bp)
app.register_blueprint(events_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(other_bp)
firestore_init.init()
app.config['db'] = FirestoreDB()
app.config['user'] = None

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
