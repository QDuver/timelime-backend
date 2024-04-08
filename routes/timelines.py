import json
import sys
from flask import Blueprint, request
import datetime, time
from decorators.decorators import  premium_required, print_full_exception, auth_required, error_handler
import utils.event_methods as event_methods
from ai import generate_timeline
from models.exceptions import CustomException
import config as c

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route("/timelines", endpoint="get_timelines")
@error_handler
@auth_required
def get_timelines():
    timelines = c.db.get("timelines", where=('uid', '==', c.user.uid), order_by=('lastUsed', 'DESCENDING'))
    return json.dumps(timelines)

@timeline_bp.route("/timeline/<timeline_id>", endpoint="get_timeline")
@error_handler
@auth_required
def get_timeline(timeline_id):

    timeline = c.db.get("timelines", doc=timeline_id)
    if(not timeline):
        raise CustomException('backend.timelineNotFound')
    timeline = _process_timeline(timeline)
    return json.dumps(timeline)

def _process_timeline(timeline):
    timeline['lastUsed'] = int(time.time())
    timeline['isEditable'] = True
    try:
        c.db.edit("timelines", timeline.id, timeline)
    except: 
        pass

    if(c.user.uid != timeline['uid']):
        if(c.user.isAnonymous and len(timeline['uid']) < 12):
            raise CustomException('backend.timelineExpired')
        if(not timeline['isPublic']):
            raise CustomException('backend.timelinePrivate')
        else:
            timeline['isEditable'] = False
    
    return timeline

@timeline_bp.route("/duplicate-timeline", endpoint="duplicate_timeline", methods=['POST'])
@auth_required
@error_handler
def duplicate_timeline():
    c.user.is_quotas_exceeded('timelines')
    timeline = request.json['timeline']
    new_timeline = create_new_timeline(timeline['name'] + ' (copy)', 'manual')
    new_timeline = _process_timeline(new_timeline)
    events = c.db.get("events", where=('tid', '==', timeline['id']))
    
    categories = c.db.get("categories", where=('tid', '==', timeline['id']))

    category_mapping = {}
    for category in categories:
        category_id = category['id']
        del category['id']
        category['tid'] = new_timeline['id']
        category['uid'] = c.db.uid
        new_id = c.db.add("categories", category)
        category_mapping[category_id] = new_id
    for event in events:
        event['tid'] = new_timeline['id']
        event['uid'] = c.db.uid
        if 'categoryId' in event and event['categoryId'] is not None:
            event['categoryId'] = category_mapping[event['categoryId']]            
        del event['id'] 
    c.db.add_batch("events", events)
    return json.dumps(new_timeline)

@timeline_bp.route("/timeline", endpoint="edit_timeline", methods=['PUT'])
@auth_required
@error_handler
def edit_timeline():
    timeline = request.json
    c.db.edit("timelines", timeline['id'], timeline)
    timeline = c.db.get("timelines", doc=timeline['id'])
    timeline = _process_timeline(timeline)
    return json.dumps(timeline)



@timeline_bp.route("/timeline", endpoint="create_timeline", methods=['POST'])
@auth_required
@error_handler
def create_timeline():
    req = request.json #for some reason if I remove this, won't work
    c.user.is_quotas_exceeded('timelines')
    timeline = create_new_timeline(generate_timeline_name(), 'manual')
    timeline = _process_timeline(timeline)
    today = {'uid': c.db.uid, 'tid': timeline['id'], 'name': f'Today', 'startDate': datetime.datetime.now().strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    yesterday = {'uid': c.db.uid, 'tid': timeline['id'], 'name': f'Yesterday', 'startDate': (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), 'categoryColor': '', 'categoryName': '', 'isDefault': True}
    default_events = event_methods.create_events([today, yesterday])
    c.db.add_batch('events', default_events)
    return json.dumps(timeline)




@timeline_bp.route("/ai-timeline", endpoint="create_ai_timeline", methods=['POST'])
@auth_required
@premium_required('timeline')
@error_handler
def create_ai_timeline():
    timeline = create_ai_timeline_(request.json['timelineName'], request.json['nEvents'], request.json['lang'], request.json['imageAssociation'])
    return json.dumps(timeline)

@timeline_bp.route("/timeline/<timeline_id>", endpoint="delete_timeline", methods=['DELETE'])
@auth_required
@error_handler
def delete_timeline(timeline_id):
    c.db.delete("timelines", timeline_id)
    return json.dumps({})

def generate_timeline_name():
    n_timelines = len(c.db.get("timelines", where=('uid', '==', c.db.uid)))
    name = 'My new timeline' if n_timelines == 0 else f'My new timeline ({n_timelines + 1})'
    return name



def create_new_timeline(name, source):
    timeline = {'uid': c.db.uid, 'name': name, 'isPublic': False, 'lastUsed': int(time.time()), 'source': source}
    timeline['id'] = c.db.add("timelines", timeline)
    return timeline

def create_ai_timeline_(timelineName, nEvents, lang, image_association, test=False):

    if(image_association == True):
        event['imageURL'] = event_methods.get_google_images(event['name'], timelineName, event['startDate'])[0]
    try:
        events = generate_timeline.main(timelineName, nEvents, lang)
        timeline = create_new_timeline(timelineName, 'ai')
        for event in events:
            event['uid'] = c.db.uid
            event['tid'] = timeline['id']
        c.db.add_batch('events', events)
        return timeline
    except Exception as e:
        print_full_exception(e)
        raise Exception("Error generating timeline")