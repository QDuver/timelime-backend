
from flask import Blueprint, jsonify, request, current_app as app, copy_current_request_context
from decorators.decorators import error_handler
from utils import image_methods
playground_bp = Blueprint('playground', __name__)
import sys
from models.user import User

@playground_bp.route("/playground/", endpoint="test", methods=['POST'])
@error_handler
def playground():

    user = User(uid='0Gu3S71O2Thq0bSv5DTY7pszf1P2')
    print('current_user', user.get_user().__dict__)


    # event = db.get('events', where= ('tid', '==', 'lYSxp2HDrJO03m4EwVKc'))[0]
    # print(event, file=sys.stderr)
    # image_methods.generate_image('google', event)
    # # image_methods.get_google_image(event)
    # print('coucou', file=sys.stderr)
    # # print(request, flush=True)
    return jsonify('coucou'), 200