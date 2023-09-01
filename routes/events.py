
import json
from flask import Blueprint, request, current_app as app
from decorators.decorators import token_required, generic_error_handler
import utils.events as events

events_bp = Blueprint('events', __name__)

@events_bp.route("/events/<timeline_id>", endpoint="get_events")
@token_required
# @generic_error_handler
def get_events(timeline_id):
    ev = events.get_events(timeline_id)
    return json.dumps(ev)

@events_bp.route("/events", endpoint="post_event", methods=['POST'])
@token_required
@generic_error_handler
def post_event():
    event = request.json
    events.create_or_edit_event(event)
    return json.dumps(event)


@events_bp.route("/event/<event_id>", endpoint="delete_event", methods=['DELETE'])
@token_required
# @generic_error_handler
def delete_event(event_id):
    app.config['db'].delete("events", event_id)
    return json.dumps({})


@events_bp.route("/categories/<timeline_id>", endpoint="get_categories", methods=['GET'])
@token_required
@generic_error_handler
def get_categories(timeline_id):
    categories = app.config['db'].get("categories", where=('tid', '==', timeline_id))
    return json.dumps(categories)

@events_bp.route("/categories/<catgory_id>", endpoint="delete_category", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_category(catgory_id):
    app.config['db'].delete("categories", catgory_id)
    events = app.config['db'].get("events", where=('category', '==', catgory_id))
    for event in events:
        event['categoryId'] = None
        events.create_or_edit_event(event)

    return json.dumps({})