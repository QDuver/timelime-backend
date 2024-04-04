
from flask import Blueprint, jsonify, request, current_app as app, copy_current_request_context
from decorators.decorators import error_handler
from config import db
from utils import image_methods
playground_bp = Blueprint('playground', __name__)
import sys

@playground_bp.route("/playground/", endpoint="test", methods=['POST'])
@error_handler
def playground():
    event = db.get('events', where= ('tid', '==', 'lYSxp2HDrJO03m4EwVKc'))[0]
    print(event, file=sys.stderr)
    image_methods.generate_image('google', event)
    # image_methods.get_google_image(event)
    print('coucou', file=sys.stderr)
    # print(request, flush=True)
    return jsonify('coucou'), 200