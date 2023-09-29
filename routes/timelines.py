import json
from flask import Blueprint, jsonify, request, current_app as app
import datetime, time
from decorators.decorators import  premium_required, print_full_exception, token_required, generic_error_handler
from models.user import User
from utils.constants import DEFAULT_QUOTAS
import utils.event_methods as event_methods
import utils.utils as utils
from ai import generate_timeline

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route("/timelines", endpoint="get_timelines")
@generic_error_handler
@token_required
def get_timelines():
    db = app.config['db']
    user = db.user
    timelines = db.get("timelines", where=('uid', '==', user.uid), order_by=('lastUsed', 'DESCENDING'))
    return json.dumps(timelines)

@timeline_bp.route("/timeline/<timeline_id>", endpoint="get_timeline")
@generic_error_handler
@token_required
def get_timeline(timeline_id):
    db = app.config['db']

    timeline = db.get("timelines", doc=timeline_id)
    if(not timeline):
        return jsonify({"message": "Timeline not found"}), 403
    try:
        timeline = _process_timeline(timeline)
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403
    return json.dumps(timeline)

def _process_timeline(timeline):
    db = app.config['db']
    user = db.user
    timeline['lastUsed'] = int(time.time())
    timeline['isEditable'] = True
    try:
        db.edit("timelines", timeline.id, timeline)
    except: 
        pass

    if(user.uid != timeline['uid']):
        if(user.isAnonymous and len(timeline['uid']) < 12):
            raise PermissionError('This timeline has expired. Login to save your progress - Handle FE')
        if(not timeline['isPublic']):
            raise PermissionError('This timeline is private')
        else:
            timeline['isEditable'] = False
    
    return timeline

@timeline_bp.route("/timeline", endpoint="edit_timeline", methods=['PUT'])
@token_required
@generic_error_handler
def edit_timeline():
    db = app.config['db']
    timeline = request.json
    db.edit("timelines", timeline['id'], timeline)
    timeline = db.get("timelines", doc=timeline['id'])
    timeline = _process_timeline(timeline)
    return json.dumps(timeline)



@timeline_bp.route("/timeline", endpoint="create_timeline", methods=['POST'])
@token_required
@generic_error_handler
def create_timeline():
    db = app.config['db']
    req = request.json #for some reason if I remove this, won't work
    if(utils.timeline_quotas_exceeded()):
        return jsonify({"message": f"You can create only {DEFAULT_QUOTAS['timelines_free']} timelines with the Free plan - Handle FE"}), 403
    timeline = create_new_timeline(generate_timeline_name(), 'manual')
    today = {'uid': db.uid, 'tid': timeline['id'], 'name': f'Today', 'startDate': datetime.datetime.now().strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    yesterday = {'uid': db.uid, 'tid': timeline['id'], 'name': f'Yesterday', 'startDate': (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    default_events = event_methods.create_events([today, yesterday])
    db.add_batch('events', default_events)
    return json.dumps(timeline)




@timeline_bp.route("/ai-timeline", endpoint="create_ai_timeline", methods=['POST'])
@token_required
@premium_required('timeline')
@generic_error_handler
def create_ai_timeline():
    utils.abort_if_already_ai_generating()
    timeline = create_ai_timeline_(request.json['timelineName'], request.json['nEvents'], request.json['imageAssociation'])
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
    n_timelines = len(db.get("timelines", where=('uid', '==', db.uid)))
    name = 'My new timeline' if n_timelines == 0 else f'My new timeline ({n_timelines + 1})'
    return name



def create_new_timeline(name, source):
    db = app.config['db']
    timeline = {'uid': db.uid, 'name': name, 'isPublic': False, 'lastUsed': int(time.time()), 'source': source}
    timeline['id'] = db.add("timelines", timeline)
    return timeline

def create_ai_timeline_(timelineName, nEvents, image_association):
    db = app.config['db']
    db.user.update_ai_tracking_status('timeline', True)
    try:
        events = generate_timeline.main(timelineName, nEvents, image_association)
        if(len(events) < 1):
            raise Exception("No events generated")
        timeline = create_new_timeline(timelineName, 'ai')
        for event in events:
            event['tid'] = timeline['id']
        db.add_batch('events', events)        
        db.user.update_ai_tracking_status('timeline', False, timeline)
        return timeline
    except Exception as e:
        print_full_exception(e)
        db.user.update_ai_tracking_status('timeline', False)
        raise Exception("Error generating timeline")