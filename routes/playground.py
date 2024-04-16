
import json
from flask import Blueprint, jsonify, request
from utils.decorators import error_handler
from routes.timelines import generate_ai_timeline
from utils.timelines import process_ai_events
playground_bp = Blueprint('playground', __name__)
from models.user import User
import config as c
from utils.images import generate_image


@playground_bp.route("/playground/", endpoint="test", methods=['POST'])
@error_handler
def playground():
    global events

    User(uid='0Gu3S71O2Thq0bSv5DTY7pszf1P2')
    events = c.db.get("events", where=('tid', '==', 'aHk5Zi37wxii7Q43MHuL'))[:2]
    for event in events:
        generate_image('ai', event)

    return jsonify('coucou'), 200