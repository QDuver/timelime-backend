
import json
from flask import Blueprint, request, current_app as app, Response, send_file, jsonify
from decorators.decorators import token_required, generic_error_handler
import utils.methods as methods
import pandas as pd
import io
events_bp = Blueprint('events', __name__)
HEADERS_MANDATORY = ['name', 'startDate']
HEADERS_OPTIONAL = ['endDate', 'description', 'categoryName', 'categoryColor', 'imageURL',]

@events_bp.route("/download-headers", endpoint="download_headers")
@token_required
@generic_error_handler
def download_headers():
    return json.dumps({'mandatory': HEADERS_MANDATORY, 'optional': HEADERS_OPTIONAL})

@events_bp.route("/download/<timeline_id>", endpoint="download_events")
@token_required
@generic_error_handler
def download_events(timeline_id):
    headers = HEADERS_MANDATORY + HEADERS_OPTIONAL

    ev = methods.get_events(app.config['db'] ,timeline_id)
    df = pd.read_json(json.dumps(ev['events']))
    if('isEndEvent' in df.columns):
        df = df[df['isEndEvent'] != True]
    if('isStepDate' in df.columns):
        df = df[df['isStepDate'] != True]
    csv_data = df[headers].to_csv(index=False)
    response = Response(csv_data, content_type='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
    return response


@events_bp.route("/events/<timeline_id>", endpoint="get_events")
@token_required
@generic_error_handler
def get_events(timeline_id):
    ev = methods.get_events(app.config['db'] ,timeline_id)
    return json.dumps(ev)

@events_bp.route("/create-event", endpoint="create_event", methods=['POST'])
@token_required
@generic_error_handler
def create_event():
    event = json.loads(request.form.get('event'))
    event = methods.create_events([event])[0]
    event_id = app.config['db'].add('events', event)
    event['id'] = event_id
    methods.handle_image(request, event)
    return json.dumps(event)


@events_bp.route("/create-events", endpoint="create_events", methods=['POST'])
@token_required
@generic_error_handler
def create_events():
    db = app.config['db']
    processed_events = methods.create_events(request.json)
    db.add_batch('events', processed_events)
    return jsonify('success')

@events_bp.route("/event", endpoint="edit_event", methods=['PUT'])
@token_required
@generic_error_handler
def edit_event():
    event = json.loads(request.form.get('event'))
    event = methods.edit_event(event)
    app.config['db'].edit('events', event['id'], {**event, 'isDefault': False})
    methods.handle_image(request, event)
    return json.dumps(event)

@events_bp.route("/generate-image", endpoint="generate_image", methods=['POST'])
@token_required
# @generic_error_handler
def generate_image():
    event = methods.generate_image(request.json)
    return json.dumps(event)

@events_bp.route("/event/<event_id>", endpoint="delete_event", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_event(event_id):
    app.config['db'].delete("events", event_id)
    return json.dumps({})


@events_bp.route("/categories/<timeline_id>", endpoint="get_categories", methods=['GET'])
@token_required
@generic_error_handler
def get_categories(timeline_id):
    categories = app.config['db'].get("categories", where=('tid', '==', timeline_id))
    return json.dumps(categories)

@events_bp.route("/categories/<category_id>", endpoint="delete_category", methods=['DELETE'])
@token_required
@generic_error_handler
def delete_category(category_id):
    app.config['db'].delete("categories", category_id)
    events = app.config['db'].get("events", where=('category', '==', category_id))
    for event in events:
        event['categoryId'] = None
        events.edit_event(event)
    return json.dumps({})
