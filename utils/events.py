from functools import cmp_to_key
from flask import current_app as app
import time 
from googleapiclient.discovery import build
import time

def create_or_edit_event(event):
    event['uid'] = app.config['user']['uid']
    if('categoryId' in event and event['categoryId']):
        app.config['db'].edit('categories', event['categoryId'], {'color': event['categoryColor'], 'name': event['categoryName']})   
    else:
        event['categoryId'] = app.config['db'].add('categories', {'color': event['categoryColor'], 'name': event['categoryName'], 'tid': event['tid'], 'uid': event['uid']})

    event.pop('categoryColor', None)
    event.pop('categoryName', None)
    if('id' in event and event['id']):
        app.config['db'].edit('events', event['id'], {**event, 'isDefault': False})
    else:
        event.pop('id', None)
        event['lastUsed'] = int(time.time())
        app.config['db'].add('events', event)

def set_to_highlight(events):
    filtered = [e for e in events if "lastUsed" in e and not e['isDefault']]
    if(len(filtered) < 1):
        return events
    lastUsedEvent = max(filtered, key=lambda x: x["lastUsed"])
    for event in events:
        event['toHighlight'] = False
        if(event == lastUsedEvent):
            event['toHighlight'] = ((time.time() - event['lastUsed']) < 10)
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
    return {'events': events, 'categories': categories}


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


def get_google_images(eventName):
    API_KEY = "AIzaSyBl9-P8iSKJ_VXNAFnaaFPqb1XNaWVeluI"
    SEARCH_ENGINE_ID = "90d862b25c6fc454e"

    service = build("customsearch", "v1", developerKey=API_KEY)
    result = service.cse().list(q=eventName, cx=SEARCH_ENGINE_ID, searchType="image", num=1).execute()
    links = [link['link'] for link in result.get("items", [])]
    return links