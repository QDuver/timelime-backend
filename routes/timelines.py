import json
from flask import Blueprint, jsonify, request, current_app as app
import datetime, time
from decorators.decorators import token_required, generic_error_handler
import utils.events as events
from ai import generate_timeline, process_timeline
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
    timeline = _process_timeline(db, timeline)
    return json.dumps(timeline)


@timeline_bp.route("/timeline", endpoint="edit_timeline", methods=['PUT'])
@token_required
@generic_error_handler
def edit_timeline():
    db = app.config['db']
    timeline = request.json
    db.edit("timelines", timeline['id'], timeline)
    timeline = db.get("timelines", doc=timeline['id'])
    timeline = _process_timeline(db, timeline)
    return json.dumps(timeline)

@timeline_bp.route("/timeline", endpoint="create_timeline", methods=['POST'])
@token_required
@generic_error_handler
def create_timeline():
    db = app.config['db']
    req = request.json #for some reason if I remove this, won't work
    timeline = create_new_timeline(generate_timeline_name(), 'manual')
    today = {'uid': app.config['user']['uid'], 'tid': timeline['id'], 'name': f'Today', 'startDate': datetime.datetime.now().strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    yesterday = {'uid': app.config['user']['uid'], 'tid': timeline['id'], 'name': f'Yesterday', 'startDate': (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    events.create_or_edit_event(today)
    events.create_or_edit_event(yesterday)
    return json.dumps(timeline)


@timeline_bp.route("/ai-timeline", endpoint="create_ai_timeline", methods=['POST'])
@token_required
@generic_error_handler
def create_ai_timeline():
    db = app.config['db']
    estimated_time = request.json['estimatedTime']
    start_time = time.time()
    db.edit('users', db.authedUser['uid'], {'generating': {'timeline' : {'loading': True, 'estimatedTime': -1 }}})
    try:
        theme = request.json['theme']
        generate_timeline.main(theme, request.json['nEvents'])
        events = process_timeline.generate_events(theme, request.json['imageAssociation'])
        if(len(events) < 1):
            raise Exception("No events generated")
        timeline = create_new_timeline(theme, 'ai')
        generation_time = time.time() - start_time
        db.edit('timelines', timeline['id'], {'generationTime': generation_time, 'estimatedTime': estimated_time})
        db.edit('users', db.authedUser['id'], {'generating': {'timeline' : {'loading': False, 'estimatedTime': None }}})
        for event in events:
            event['tid'] = timeline['id']
        db.add_batch('events', events)        
    except Exception as e:
        print(e, flush=True)
        db.edit('users', db.authedUser['id'], {'generating': {'timeline' : {'loading': False, 'estimatedTime': None }}})
        return jsonify({"message": "Error generating timeline"}), 400
    return json.dumps(timeline)

@timeline_bp.route("/timeline/<timeline_id>", endpoint="delete_timeline", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_timeline(timeline_id):
    db = app.config['db']
    db.delete("timelines", timeline_id)
    return json.dumps({})

def generate_timeline_name():
    db = app.config['db']
    n_timelines = len(db.get("timelines", where=('uid', '==', app.config['user']['uid'])))
    name = 'My new timeline' if n_timelines == 0 else f'My new timeline ({n_timelines + 1})'
    return name

def create_new_timeline(name, source):
    db = app.config['db']
    timeline = {'uid': app.config['user']['uid'], 'name': name, 'isPublic': False, 'lastUsed': int(time.time()), 'source': source}
    timeline['id'] = db.add("timelines", timeline)
    return timeline

def _process_timeline(db, timeline):
    timeline['lastUsed'] = int(time.time())
    timeline['isEditable'] = True
    try:
        db.edit("timelines", timeline.id, timeline)
    except: 
        pass

    if(db.authedUser['uid'] != timeline['uid']):
        if(db.is_anonymous_user() and len(timeline['uid']) < 12):
            raise Exception('This timeline has expired. Login to save your progress')
        if(not timeline['isPublic']):
            raise Exception('This timeline is private')
        else:
            timeline['isEditable'] = False
    
    return timeline