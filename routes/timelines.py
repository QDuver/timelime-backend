import json
from flask import Blueprint, request
from utils.decorators import  premium_required, auth_required, error_handler
import config as c
from utils.timelines import create_new_timeline, generate_timeline_name, update_timeline, generate_ai_timeline, check_timeline_accessibility
from utils.events import duplicate_categories, duplicate_events, create_default_events

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
    timeline = check_timeline_accessibility(timeline)
    timeline = update_timeline(timeline)
    return json.dumps(timeline)

@timeline_bp.route("/duplicate-timeline", endpoint="duplicate_timeline", methods=['POST'])
@auth_required
@error_handler
def duplicate_timeline():
    c.user.is_quotas_exceeded('timelines')
    old_timeline = request.json['timeline']
    new_timeline = create_new_timeline(old_timeline['name'] + ' (copy)', 'manual')
    duplicated_categories = duplicate_categories(old_timeline, new_timeline)
    duplicated_events = duplicate_events(old_timeline, duplicated_categories)
    c.db.add_batch("events", duplicated_events)
    return json.dumps(new_timeline)

@timeline_bp.route("/timeline", endpoint="edit_timeline", methods=['PUT'])
@auth_required
@error_handler
def edit_timeline():
    timeline = request.json
    c.db.edit("timelines", timeline['id'], timeline)
    timeline = c.db.get("timelines", doc=timeline['id'])
    timeline = update_timeline(timeline)
    return json.dumps(timeline)

@timeline_bp.route("/manual-timeline", endpoint="create_manual_timeline", methods=['POST'])
@auth_required
@error_handler
def create_manual_timeline():
    req = request.json #for some reason if I remove this, won't work
    c.user.is_quotas_exceeded('timelines')
    timeline_name = generate_timeline_name()
    timeline = create_new_timeline(timeline_name, 'manual')
    timeline = update_timeline(timeline)
    default_events = create_default_events(timeline)
    c.db.add_batch('events', default_events)
    return json.dumps(timeline)

@timeline_bp.route("/ai-timeline", endpoint="create_ai_timeline", methods=['POST'])
@auth_required
@premium_required('timeline')
@error_handler
def create_ai_timeline():
    timeline = generate_ai_timeline(request.json['timelineName'], request.json['nEvents'], request.json['lang'])
    return json.dumps(timeline)

@timeline_bp.route("/timeline/<timeline_id>", endpoint="delete_timeline", methods=['DELETE'])
@auth_required
@error_handler
def delete_timeline(timeline_id):
    c.db.delete("timelines", timeline_id)
    return json.dumps({})

