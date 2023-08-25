import json
from flask import Blueprint, jsonify, request, current_app as app
import datetime, time
from decorators import token_required, generic_error_handler
import utils.events as events

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route("/timelines", endpoint="get_timelines")
@token_required
# @generic_error_handler
def get_timelines():
    timelines = app.config['db'].get("timelines", where=('uid', '==', app.config['user']['uid']), order_by=('lastUsed', 'DESCENDING'))
    return json.dumps(timelines)

@timeline_bp.route("/timeline/<timeline_id>", endpoint="get_timeline")
@token_required
@generic_error_handler
def get_timeline(timeline_id):
    doc = app.config['db'].get("timelines", doc=timeline_id)
    doc['lastUsed'] = int(time.time())
    try:
        app.config['db'].edit("timelines", timeline_id, doc)
    except: 
        pass

    if(app.config['db'].authedUser['uid'] != doc['uid']):
        if(not doc['isPublic']):
            return jsonify({"message": "This timeline can only be viewed by its owner"}), 401
        else:
            doc['isEditable'] = False
    return json.dumps(doc)


@timeline_bp.route("/timeline", endpoint="edit_timeline", methods=['PUT'])
@token_required
@generic_error_handler
def edit_timeline():
    timeline = request.json
    app.config['db'].edit("timelines", timeline['id'], timeline)
    return json.dumps(timeline)

@timeline_bp.route("/timeline", endpoint="create_timeline", methods=['POST'])
@token_required
# @generic_error_handler
def create_timeline():
    req = request.json #for some reason if I remove this, won't work
    print(app.config['user'], flush=True)
    timeline = {'uid': app.config['user']['uid'], 'name': 'New timeline', 'isPublic': False, 'lastUsed': int(time.time())}
    timeline['id'] = app.config['db'].add("timelines", timeline)
    default_event = {'uid': app.config['user']['uid'], 'tid': timeline['id'], 'name': 'New event', 'startDate': datetime.datetime.now().strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    events.create_or_edit_event(default_event)
    return json.dumps(timeline)


@timeline_bp.route("/timeline/<timeline_id>", endpoint="delete_timeline", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_timeline(timeline_id):
    app.config['db'].delete("timelines", timeline_id)
    return json.dumps({})