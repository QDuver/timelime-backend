import pandas as pd
from firestore.firestore_db import FirestoreDB
from firebase_admin import auth
import time
from datetime import datetime
from utils import events as events
import numpy as np

pd.set_option('display.max_columns', None)

months = {'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12}

def to_dd_mm_yyyy(newDate):
    isNegative = False
    if('-' in newDate):
        isNegative = True
        newDate = newDate.replace('-', '')
    splitted = newDate.strip().split(' ')
    newDate = splitted[-1]+'-'+splitted[-2]+'-'+splitted[-3]
    if(isNegative):
        newDate = '-'+newDate
    
    return newDate

def month_to_num(newDate):
    for month in months:
        if(month in newDate):
            newDate = newDate.replace(month, str(months[month]))
            newDate = to_dd_mm_yyyy(newDate.strip())
    return newDate

def handle_century(newDate):
    if('th century' in newDate):
        newDate = newDate.split('th century')[0]+'00'
    return newDate



def process_date(date):
    if(date == None): return None
    newDate = date.lower().strip()
    if('ac' in newDate): 
        newDate = '-'+newDate.replace('ac', '')
    if('bc' in newDate): 
        newDate = '-'+newDate.replace('bc', '')
    if('ad' in newDate):
        newDate = newDate.replace('ad', '')

    if(any(month in newDate for month in months)):
        newDate = month_to_num(newDate)
    
    newDate = handle_century(newDate)   
    if(newDate == 'present'):
        newDate = datetime.now().year

    return str(newDate).strip()


def process(df):
    df['startDate'] = df['startDate'].apply(lambda x: process_date(x))
    df['endDate'] = df['endDate'].apply(lambda x: process_date(x))
    return df


def upload(name, title):
    df = pd.read_csv('ai/generated/'+name+'.csv', index_col=False)
    df = df.replace({np.nan: None})
    df = process(df)

    db = FirestoreDB()
    user = auth.get_user_by_email('timelines.contact@gmail.com').__dict__['_data']
    user['uid'] = user['localId']
    db.set_user(user)

    timeline = {'uid': user['uid'], 'name': title, 'isPublic': True, 'lastUsed': int(time.time())}
    timeline['id'] = db.add("timelines", timeline)
    print('created', timeline['id'])
    for i, row in df.iterrows():
        event = {'uid': user['uid'], 'tid': timeline['id'], 'name': row['name'], 'startDate': row['startDate'], 'description': row['description'], 'endDate': row['endDate']}
        event['imageURL'] = events.get_google_images(row['name'])[0]
        print(event)
        db.add('events', event)