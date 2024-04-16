
# import warnings
# warnings.filterwarnings("ignore", category=UserWarning)



import time
import flask
from flask_cors import CORS

from routes.websockets import register_socket_events
app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

from flask_socketio import SocketIO, emit
socketio = SocketIO(app, cors_allowed_origins="*")

import config
config.set_env_vars()
config.init_firebase()
config.init_limiter(app)
config.init_db()

from routes import timeline_bp, events_bp, auth_bp, other_bp, payment_bp, quizzes_bp, playground_bp
blueprints = [timeline_bp, events_bp, auth_bp, other_bp, payment_bp, quizzes_bp, playground_bp]
for bp in blueprints:
    app.register_blueprint(bp)
register_socket_events(socketio)



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)