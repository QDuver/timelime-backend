from utils.utils import generate_random_id, set_env_variables
set_env_variables()
import firestore.firestore_init as firestore_init
firestore_init.init()
import uuid
import flask
from flask_cors import CORS
from decorators.decorators import limiter
import warnings
from routes import timeline_bp, events_bp, auth_bp, other_bp, payment_bp, quizzes_bp

warnings.filterwarnings("ignore", category=UserWarning)
app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
limiter.init_app(app)

import config
config.init()

# app.config['session'] = generate_random_id()


app.register_blueprint(timeline_bp)
app.register_blueprint(events_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(other_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(quizzes_bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
