
# import warnings
# warnings.filterwarnings("ignore", category=UserWarning)



import flask
from flask_cors import CORS
app = flask.Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

import config
config.set_env_vars()
config.init_firebase()
config.init_limiter(app)
config.init_db()

from routes import timeline_bp, events_bp, auth_bp, other_bp, payment_bp, quizzes_bp, playground_bp
blueprints = [timeline_bp, events_bp, auth_bp, other_bp, payment_bp, quizzes_bp, playground_bp]
for bp in blueprints:
    app.register_blueprint(bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
