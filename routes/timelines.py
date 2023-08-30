import json
from flask import Blueprint, jsonify, request, current_app as app
import datetime, time
from decorators import token_required, generic_error_handler
import utils.events as events
from utils import utils

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route("/timelines", endpoint="get_timelines")
@token_required
@generic_error_handler
def get_timelines():
    db = app.config['db']
    timelines = db.get("timelines", where=('uid', '==', app.config['user']['uid']), order_by=('lastUsed', 'DESCENDING'))
    return json.dumps(timelines)

@timeline_bp.route("/timeline/<timeline_id>", endpoint="get_timeline")
@token_required
@generic_error_handler
def get_timeline(timeline_id):
    db = app.config['db']
    timeline = db.get("timelines", doc=timeline_id)
    if(not timeline):
        return jsonify({"message": "Timeline not found"}), 404
    timeline = process_timeline(db, timeline)
    return json.dumps(timeline)


@timeline_bp.route("/timeline", endpoint="edit_timeline", methods=['PUT'])
@token_required
@generic_error_handler
def edit_timeline():
    db = app.config['db']
    timeline = request.json
    db.edit("timelines", timeline['id'], timeline)
    timeline = db.get("timelines", doc=timeline['id'])
    timeline = process_timeline(db, timeline)
    return json.dumps(timeline)

@timeline_bp.route("/timeline", endpoint="create_timeline", methods=['POST'])
@token_required
@generic_error_handler
def create_timeline():
    db = app.config['db']
    req = request.json #for some reason if I remove this, won't work
    timeline = {'uid': app.config['user']['uid'], 'name': 'New timeline', 'isPublic': False, 'lastUsed': int(time.time())}
    timeline['id'] = db.add("timelines", timeline)
    default_event = {'uid': app.config['user']['uid'], 'tid': timeline['id'], 'name': f'Day I created my new timeline', 'startDate': datetime.datetime.now().strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    events.create_or_edit_event(default_event)
    return json.dumps(timeline)


@timeline_bp.route("/timeline/<timeline_id>", endpoint="delete_timeline", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_timeline(timeline_id):
    db = app.config['db']
    db.delete("timelines", timeline_id)
    return json.dumps({})


def process_timeline(db, timeline):
    timeline['lastUsed'] = int(time.time())
    timeline['isEditable'] = True
    try:
        db.edit("timelines", timeline.id, timeline)
    except: 
        pass

    if(db.authedUser['uid'] != timeline['uid']):
        if(db.is_anonymous_user() and not timeline['isPublic']):
            raise Exception('This timeline has expired, Login to save your progress')
        if(not timeline['isPublic']):
            raise Exception('This timeline is private')
        else:
            timeline['isEditable'] = False
    
    return timeline