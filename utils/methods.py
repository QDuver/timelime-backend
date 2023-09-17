from functools import cmp_to_key
from flask import current_app as app
import time 
from googleapiclient.discovery import build
import time
from ai.dalle import generate_image
from utils.constants import DEFAULT_QUOTAS
from utils.utils import get_secret, print_full_exception
from ai import generate_timeline, process_timeline
from google.cloud import storage
import os
import re
import datetime


def event_quotas_exceeded(event):
    db = app.config['db']
    if(db.user.isPremium):
        return False
    n_events = len(db.get('events', where=('tid', '==', event['tid'])))
    if(n_events >= DEFAULT_QUOTAS['events_free']):
        return Trues

def timeline_quotas_exceeded():
    db = app.config['db']
    if(db.user.isPremium):
        return False
    n_timelines = len(db.get('timelines', where=('uid', '==', db.uid)))
    if(n_timelines >= DEFAULT_QUOTAS['timelines_free']):
        return True

def strip_leading_zeros(event):

    def handle_if_dash_as_first(date):
        if(not date):
            return '0'
        return date if date[0] != '-' else '0'+date

    event['startDate'] = handle_if_dash_as_first(event['startDate'].lstrip('0'))
    try:
        event['endDate'] = handle_if_dash_as_first(event['endDate'].lstrip('0'))
    except:
        pass
    return event

def handle_image(request, event):
    db = app.config['db']
    if('file' in request.files):
        bucket_name = os.environ.get('TIMELIME_USER_IMAGES_BUCKET', 'timelime-dev-user-images-bucket')
        file = request.files['file']
        gcs = storage.Client()
        bucket = gcs.get_bucket(bucket_name)
        blob = bucket.blob(event['id'])
        blob.upload_from_string( file.read(), content_type=file.content_type )
        event['imageName'] = event['imageURL']
        event['imageURL'] = f'https://storage.cloud.google.com/{bucket_name}/{event["id"]}'
        db.edit('events', event['id'], event)
    if('imageURL' in event and 'An AI image will start' in event['imageURL']):
        event['imageGenerating'] = True
        db.edit('events', event['id'], event)


def create_or_edit_preprocessing(event, categories = None):
    if not (categories):
        categories = app.config['db'].get('categories', where=('tid', '==', event['tid']))

    if('categoryId' in event and event['categoryId']): #if category exists, but in case color or name may have changed
        app.config['db'].edit('categories', event['categoryId'], {'color': event['categoryColor'], 'name': event['categoryName']})   

    elif('categoryName' in event and 'categoryColor' in event and event['categoryName'] and event['categoryColor']): #presence of categoryName and Color but no categoryId, check if one already exists
        foundCategory = False
        for category in categories:
            if(category['name'] == event['categoryName'] and category['color'] == event['categoryColor']):
                event['categoryId'] = category['id']
                foundCategory = True
                break
        if(not foundCategory):
            event['categoryId'] = app.config['db'].add('categories', {'color': event['categoryColor'], 'name': event['categoryName'], 'tid': event['tid'], 'uid': db.uid})

    event.pop('categoryColor', None)
    event.pop('categoryName', None)
    event = strip_leading_zeros(event)

    if('endDate' not in event):
        event['endDate'] = None
    if('description' not in event):
        event['description'] = None
    
    event['lastUsed'] = int(time.time())
    return event
    

def create_events(events):
    db = app.config['db']
    for event in events:
        for key in list(event.keys()):
            if ' (optional)' in key:
                event[key.replace(' (optional)', '')] = event.pop(key)

    categories = db.get('categories', where=('tid', '==', events[0]['tid']))
    processed_events = []
    for event in events:
        event['uid'] = db.uid
        event = create_or_edit_preprocessing(event, categories)
        processed_events.append(event)
    return processed_events


def edit_event(event):
    return create_or_edit_preprocessing(event)

def set_to_highlight(events):
    filtered = [e for e in events if "lastUsed" in e]
    if(len(filtered) < 1):
        return events
    lastUsedEvent = max(filtered, key=lambda x: x["lastUsed"])
    for event in events:
        event['toHighlight'] = False
        if(event == lastUsedEvent):
            if('isDefault' in event and event['isDefault']):
                break
            event['toHighlight'] = ((time.time() - event['lastUsed']) < 10)
    return events

def assign_none_to_empty(events):
    optional_cols = ['endDate', 'description', 'imageURL', 'categoryName', 'categoryColor']
    for event in events:
        for col in optional_cols:
            if(col not in event):
                event[col] = ''
    return events

def get_events(db, timeline_id):    
    start = time.time()
    events = db.get('events', where=('tid', '==', timeline_id))
    events = [event for event in events if 'name' in event and 'startDate' in event and event['startDate']]
    if(len(events) < 1):
        return {'events': [], 'categories': []}
    categories = db.get('categories', where=('tid', '==', timeline_id))
    categories = [category for category in categories if 'name' in category and category['name']]
    events = merge_with_categories(events, categories)
    events = create_end_events(events)
    events = sorted(events, key=cmp_to_key(custom_sort))
    events = set_to_highlight(events)
    events = create_step_dates(events)
    events = sorted(events, key=cmp_to_key(custom_sort))
    events = set_scaling(events)
    events = assign_none_to_empty(events)
    events = process_image(events)
    return {'events': events, 'categories': categories}


def process_image(events):
    for event in events:
        if('imageURL' in event and event['imageURL'] and 'An AI image will start' in event['imageURL']):
            event['imageURL'] = ''
    return events


def set_scaling(events):
    if(len(events) < 3):
        return events
    for event in events:
        event['dateInDays'] = date_to_days(split_date(event['startDate'], 1))
    totalDiffs = 0
    for i, event in enumerate(events):
        event['previousEventDiff'] = 0
        if(i > 0):
            diff = event['dateInDays'] - events[i-1]['dateInDays']
            totalDiffs += diff
            event['previousEventDiff'] = diff

    maxHeight = len(events) * 25 * 3
    for event in events:
        ratio = event['previousEventDiff'] / totalDiffs
        event['previousEventDistance'] = int(ratio * maxHeight)

    return events

def create_step_dates(events):
    possible_gaps = [10000000000, 1000000000, 10000000, 1000000, 100000, 10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10, 5, 2, 1]
    unique_event_years = list(set([split_date(event['startDate'])['year'] for event in events]))
    first_year = split_date(events[0]['startDate'])['year']
    last_year = split_date(events[-1]['startDate'])['year']
    absolute_gap = last_year - first_year
    gap_to_events = absolute_gap / (len(events) / 4)
    step = min(possible_gaps, key=lambda x:abs(x-gap_to_events))
    all_step_dates = []
    for i in range(0, first_year, -step):
        all_step_dates.append(i)
    for i in range(0, last_year, step):
        all_step_dates.append(i)
    all_step_dates = list(set([date for date in all_step_dates if date > first_year and date < last_year and date not in unique_event_years]))
    for date in all_step_dates:
        events.append({
            "name": str(date),
            "startDate": str(date),
            "isStepDate": True,
        })
    return events

def merge_with_categories(events, categories):
    for event in events:
        for category in categories:
            if('categoryId' in event and event['categoryId'] == category['id']):
                event['categoryColor'] = category['color'] if 'color' in category and category['color'] else None
                event['categoryName'] = category['name']
                event['categoryId'] = category['id']   

        if('categoryId' in event and event['categoryId'] not in [category['id'] for category in categories]):
            event['categoryColor'] = None
            event['categoryName'] = None
            event['categoryId'] = None

    
    return events

def create_end_events(events):
    end_events = []
    for event in events:
        if('endDate' in event and event['endDate']):
            event['endEventId'] = 'end'+event['id']
            end_events.append({
                'id': 'end'+event['id'],
                'startDate': event['endDate'],
                'isEndEvent': True,
                'categoryColor': event['categoryColor'] if 'categoryColor' in event else None,
            })
    return events + end_events

def custom_sort(a, b):
    date1 = a['startDate']
    date2 = b['startDate']
    year1 = split_date(date1)['year']
    month1 = split_date(date1)['month']
    day1 = split_date(date1)['day']
    year2 = split_date(date2)['year']
    month2 = split_date(date2)['month']
    day2 = split_date(date2)['day']

    if (year1 < year2): return -1
    if (year1 > year2): return 1

    if(month1 != None and month2 != None):
        if (month1 < month2): return -1
        if (month1 > month2): return 1

    if(day1 != None and day2 != None):
        if (day1 < day2): return -1
        if (day1 > day2): return 1

    return 0


def date_to_days(date):
    return date['year'] * 365 + date['month'] * 30 + date['day']


def  split_date(date, default=None):

    date = str(date)
    isNegative = False
    if (date[0] == '-'):
        date = date[1:]
        isNegative = True
    
    rv = {
      'year': int(date.split('-')[0]) if not isNegative else int(date.split('-')[0]) * -1,
      'month': int(date.split('-')[1]) if len(date.split('-')) > 1 else default,
      'day': int(date.split('-')[2]) if len(date.split('-')) > 2 else default
    }
    return rv


def get_google_images(eventName, timelineName, num=1):
    db = app.config['db']
    try:
        API_KEY = get_secret('SEARCH_ENGINE')
        SEARCH_ENGINE_ID = "90d862b25c6fc454e"
        query = eventName + " " + timelineName if "new timeline" not in timelineName.lower() else eventName

        service = build("customsearch", "v1", developerKey=API_KEY)
        result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, searchType="image", num=num).execute()
        links = [link['link'] for link in result.get("items", [])]
        db.user.update_ai_tracking_status('search', False, True)
        return links
    except Exception as e:
        print_full_exception(e)
        raise Exception("Error getting images")


def create_new_timeline(name, source):
    db = app.config['db']
    timeline = {'uid': db.uid, 'name': name, 'isPublic': False, 'lastUsed': int(time.time()), 'source': source}
    timeline['id'] = db.add("timelines", timeline)
    return timeline

def create_ai_timeline_(timelineName, nEvents, imageAssociation):
    db = app.config['db']
    db.user.update_ai_tracking_status('timeline', True)
    try:
        generate_timeline.main(timelineName, nEvents)
        events = process_timeline.main(timelineName, imageAssociation)
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

