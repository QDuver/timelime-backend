
import json
from flask import Blueprint, request, Response, jsonify
from decorators.decorators import premium_required, print_full_exception, auth_required, error_handler
from utils import image_methods
import utils.event_methods as event_methods
import pandas as pd
from models.exceptions import CustomException
import config as c

events_bp = Blueprint('events', __name__)
HEADERS_MANDATORY = ['name', 'startDate']
HEADERS_OPTIONAL = ['endDate', 'description', 'categoryName', 'categoryColor', 'imageURL',]


@events_bp.route("/download-headers", endpoint="download_headers")
@error_handler
def download_headers():
    return json.dumps({'mandatory': HEADERS_MANDATORY, 'optional': HEADERS_OPTIONAL})

@events_bp.route("/download/<timeline_id>", endpoint="download_events")
@auth_required
@error_handler
def download_events(timeline_id):
    headers = HEADERS_MANDATORY + HEADERS_OPTIONAL

    ev = event_methods.get_events(timeline_id)
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
@auth_required
@error_handler
def get_events(timeline_id):
    ev = event_methods.get_events(timeline_id)
    return json.dumps(ev)

@events_bp.route("/create-event", endpoint="create_event", methods=['POST'])
@error_handler
@auth_required
def create_event():
    event = json.loads(request.form.get('event'))
    c.user.is_quotas_exceeded('events', event)
    event = event_methods.create_events([event])[0]
    event_id = c.db.add('events', event)
    event['id'] = event_id
    image_methods.handle_image(request, event)
    return json.dumps(event)


@events_bp.route("/upload-events", endpoint="upload_events", methods=['POST'])
@auth_required
@error_handler
def upload_events():
    try:
        processed_events = event_methods.create_events(request.json)
        c.db.add_batch('events', processed_events)
    except Exception as e:
        print_full_exception(e)
        raise CustomException("backend.errorUploadingEvents")
    return jsonify('success')

@events_bp.route("/event", endpoint="edit_event", methods=['PUT'])
@auth_required
@error_handler
def edit_event():
    event = json.loads(request.form.get('event'))
    event, _ = event_methods.create_or_edit_preprocessing(event)    
    c.db.edit('events', event['id'], {**event, 'isDefault': False})
    image_methods.handle_image(request, event)
    return json.dumps(event)

@events_bp.route("/generate-image", endpoint="generate_image", methods=['POST'])
@auth_required
@error_handler
@premium_required('image')
def generate_image():
    event = event_methods.generate_image(request.json)
    return json.dumps(event)

@events_bp.route("/event/<event_id>", endpoint="delete_event", methods=['DELETE'])
@auth_required
@error_handler
def delete_event(event_id):
    c.db.delete("events", event_id)
    return json.dumps({})


@events_bp.route("/categories/<timeline_id>", endpoint="get_categories", methods=['GET'])
@auth_required
@error_handler
def get_categories(timeline_id):
    categories = c.db.get("categories", where=('tid', '==', timeline_id))
    return json.dumps(categories)

@events_bp.route("/categories/<category_id>", endpoint="delete_category", methods=['DELETE'])
@auth_required
@error_handler
def delete_category(category_id):
    c.db.delete("categories", category_id)
    events = c.db.get("events", where=('category', '==', category_id))
    for event in events:
        event['categoryId'] = None
        event_methods.create_or_edit_preprocessing(event)
    return json.dumps({})


@events_bp.route("/google-imgs", endpoint="google_images", methods=['POST'])
@auth_required
@error_handler
@premium_required('search')
def google_images():
    links = image_methods.get_google_images(request.json['eventName'], request.json['timelineName'], request.json['startDate'])
    return jsonify({"links": links}), 200