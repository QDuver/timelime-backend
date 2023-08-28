from functools import cmp_to_key
from flask import current_app as app
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
        event_id = app.config['db'].add('events', event)

def set_to_highlight(events):
    filtered = [e for e in events if "lastUsed" in e]
    if(len(filtered) <= 1):
        return events
    lastUsedEvent = max(filtered, key=lambda x: x["lastUsed"])
    for event in events:
        event['toHighlight'] = False
        if(event == lastUsedEvent):
            event['toHighlight'] = ((time.time() - event['lastUsed']) < 5)
    return events

def get_events(timeline_id):    
    events = app.config['db'].get('events', where=('tid', '==', timeline_id))
    events = [event for event in events if 'name' in event and 'startDate' in event and event['startDate']]
    categories = app.config['db'].get('categories', where=('tid', '==', timeline_id))
    categories = [category for category in categories if 'name' in category and category['name']]
    print(events, flush=True)
    events = merge_with_categories(events, categories)
    events = create_end_events(events)
    events = sorted(events, key=cmp_to_key(custom_sort))
    events = set_to_highlight(events)
    return {'events': events, 'categories': categories}


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
    year1 = splitDate(date1)['year']
    month1 = splitDate(date1)['month']
    day1 = splitDate(date1)['day']
    year2 = splitDate(date2)['year']
    month2 = splitDate(date2)['month']
    day2 = splitDate(date2)['day']

    if (year1 < year2): return -1
    if (year1 > year2): return 1

    if(month1 != None and month2 != None):
        if (month1 < month2): return -1
        if (month1 > month2): return 1

    if(day1 != None and day2 != None):
        if (day1 < day2): return -1
        if (day1 > day2): return 1

    return 0


def  splitDate(date):
    date = str(date)
    isNegative = False
    if (date[0] == '-'):
        date = date[1:]
        isNegative = True
    
    rv = {
      'year': int(date.split('-')[0]) if not isNegative else int(date.split('-')[0]) * -1,
      'month': int(date.split('-')[1]) if len(date.split('-')) > 1 else None,
      'day': int(date.split('-')[2]) if len(date.split('-')) > 2 else None
    }
    return rv
