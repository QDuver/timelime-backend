import json
from flask import Blueprint, request, current_app as app
import datetime, time
from decorators.decorators import  premium_required, print_full_exception, token_required, error_handler
import utils.event_methods as event_methods
import utils.utils as utils
from ai import generate_timeline
from firestore.firestore_db import UnprotectedFirestoreDB
from models.exceptions import CustomException

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route("/timelines", endpoint="get_timelines")
@error_handler
@token_required
def get_timelines():
    db = app.config['db']
    user = db.user
    timelines = db.get("timelines", where=('uid', '==', user.uid), order_by=('lastUsed', 'DESCENDING'))
    return json.dumps(timelines)

@timeline_bp.route("/timeline/<timeline_id>", endpoint="get_timeline")
@error_handler
@token_required
def get_timeline(timeline_id):
    db = app.config['db']

    timeline = db.get("timelines", doc=timeline_id)
    if(not timeline):
        raise CustomException('Timeline not found')
    timeline = _process_timeline(timeline)
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

    print(timeline['uid'], user.uid, flush=True)
    if(user.uid != timeline['uid']):
        if(user.isAnonymous and len(timeline['uid']) < 12):
            raise CustomException('This timeline has expired. Login to save your progress')
        if(not timeline['isPublic']):
            raise CustomException('This timeline is private')
        else:
            timeline['isEditable'] = False
    
    return timeline

@timeline_bp.route("/duplicate-timeline", endpoint="duplicate_timeline", methods=['POST'])
@token_required
@error_handler
def duplicate_timeline():
    utils.timeline_quotas_exceeded()
    db = app.config['db']
    timeline = request.json['timeline']
    new_timeline = create_new_timeline(timeline['name'] + ' (copy)', 'manual')
    new_timeline = _process_timeline(new_timeline)
    events = db.get("events", where=('tid', '==', timeline['id']))
    
    categories = db.get("categories", where=('tid', '==', timeline['id']))
    category_mapping = {}
    for category in categories:
        category_id = category['id']
        del category['id']
        category['tid'] = new_timeline['id']
        category['uid'] = db.uid
        new_id = db.add("categories", category)
        category_mapping[category_id] = new_id
    for event in events:
        event['tid'] = new_timeline['id']
        event['uid'] = db.uid
        if 'categoryId' in event:
            event['categoryId'] = category_mapping[event['categoryId']]            
        del event['id'] 
    db.add_batch("events", events)
    return json.dumps(new_timeline)

@timeline_bp.route("/timeline", endpoint="edit_timeline", methods=['PUT'])
@token_required
@error_handler
def edit_timeline():
    db = app.config['db']
    timeline = request.json
    db.edit("timelines", timeline['id'], timeline)
    timeline = db.get("timelines", doc=timeline['id'])
    timeline = _process_timeline(timeline)
    return json.dumps(timeline)



@timeline_bp.route("/timeline", endpoint="create_timeline", methods=['POST'])
@token_required
@error_handler
def create_timeline():
    db = app.config['db']
    req = request.json #for some reason if I remove this, won't work
    utils.timeline_quotas_exceeded()
    timeline = create_new_timeline(generate_timeline_name(), 'manual')
    today = {'uid': db.uid, 'tid': timeline['id'], 'name': f'Today', 'startDate': datetime.datetime.now().strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    yesterday = {'uid': db.uid, 'tid': timeline['id'], 'name': f'Yesterday', 'startDate': (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    default_events = event_methods.create_events([today, yesterday])
    db.add_batch('events', default_events)
    return json.dumps(timeline)




@timeline_bp.route("/ai-timeline", endpoint="create_ai_timeline", methods=['POST'])
@token_required
@premium_required('timeline')
@error_handler
def create_ai_timeline():
    utils.abort_if_already_ai_generating()
    timeline = create_ai_timeline_(request.json['timelineName'], request.json['nEvents'], request.json['imageAssociation'])
    return json.dumps(timeline)

@timeline_bp.route("/timeline/<timeline_id>", endpoint="delete_timeline", methods=['DELETE'])
@token_required
@error_handler
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
    try:
        db = app.config['db']
    except:
        db = UnprotectedFirestoreDB()
    timeline = {'uid': db.uid, 'name': name, 'isPublic': False, 'lastUsed': int(time.time()), 'source': source}
    timeline['id'] = db.add("timelines", timeline)
    return timeline

def create_ai_timeline_(timelineName, nEvents, image_association, test=False):
    db = app.config['db'] if test == False else UnprotectedFirestoreDB()
    if(test == False):
        db.user.update_ai_tracking_status('timeline', True)
    try:
        events = generate_timeline.main(timelineName, nEvents, image_association)
        if(len(events) < 1):
            raise Exception("No events generated")
        timeline = create_new_timeline(timelineName, 'ai')
        for event in events:
            event['tid'] = timeline['id']
        db.add_batch('events', events)
        if(test == False):        
            db.user.update_ai_tracking_status('timeline', False, timeline)
        return timeline
    except Exception as e:
        print_full_exception(e)
        if(test == False):
            db.user.update_ai_tracking_status('timeline', False)
        raise Exception("Error generating timeline")