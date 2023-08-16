

get_events(): 
    events = db.collection('events').where("tid", "==", timeline_id).get()
    events = [dict(event.to_dict(), id=event.id) for event in events]
    events = [dict(event, isPressed = False, categoryColor = '#4a8098', categoryName = None, showCircle = False, isSticky = False ) for event in events]
    
    categories = db.collection('categories').where("tid", "==", timeline_id).get()
    categories = [dict(category.to_dict(), id=category.id) for category in categories]

    merged = []
    for event in events:
        for category in categories:
            if(event['categoryId'] == category['id']):
                event['categoryColor'] = category['color'] if 'color' in category and category['color'] != None else '#4a8098'
                event['categoryName'] = category['name']
                event['categoryId'] = category['id']
                merged.append(event)
                break
    
    print(merged, flush=True)