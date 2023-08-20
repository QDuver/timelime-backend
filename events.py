from firestore_db import FirestoreDB
from functools import cmp_to_key

def create_or_edit_event(event):
    db = FirestoreDB()
    event.pop('categoryColor', None)
    event.pop('categoryName', None)
    if('id' in event and event['id']):
        db.edit('events', event['id'], event)
    else:
        event.pop('id', None)
        db.add('events', event)




def get_events(timeline_id): 
    db = FirestoreDB()
    events = db.get('events', where=('tid', '==', timeline_id))
    events = [dict(event, isPressed = False, categoryColor = '#4a8098', categoryName = None, showCircle = False, isSticky = False ) for event in events]
    events = [event for event in events if 'name' in event and 'startDate' in event and event['startDate']]
    categories = db.get('categories', where=('tid', '==', timeline_id))
    events = merge_with_categories(events, categories)
    events = create_end_events(events)
    events = sorted(events, key=cmp_to_key(custom_sort))
    return {'events': events, 'categories': categories}


def merge_with_categories(events, categories):
    for event in events:
        for category in categories:
            if('categoryId' in event and event['categoryId'] == category['id']):
                event['categoryColor'] = category['color'] if 'color' in category and category['color'] else '#4a8098'
                event['categoryName'] = category['name']
                event['categoryId'] = category['id']

    # unassignCatIdWhereEmptyCatName
    
#   private unassignCatIdWhereEmptyCatName(events) {
#     events
#       .filter((event) => !event.categoryName && event.categoryId)
#       .map((event) => (event.categoryId = null));
#   }
    return events

def create_end_events(events):
    end_events = []
    for event in events:
        if('endDate' in event and event['endDate']):
            print('end event', event['endDate'])
            if(event['endDate'] == ''):
                print(event)
            event['endEventId'] = 'end'+event['id']
            end_events.append({
                'id': 'end'+event['id'],
                'startDate': event['endDate'],
                'isEndEvent': True,
                'categoryColor': event['categoryColor'],
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
