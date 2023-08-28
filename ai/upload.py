import pandas as pd
from firestore_db import FirestoreDB, firestore_init
from firebase_admin import auth
import time
import datetime
from utils import events as events
import numpy as np

pd.set_option('display.max_columns', None)

months = {'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12}

def month_to_num(newDate):
    for month in months:
        if(month in newDate):
            newDate = newDate.replace(month, str(months[month]))
    return newDate

def to_dd_mm_yyy(newDate):
    year = newDate.strip().split(' ')[-1]
    if(len(year) == 2):
            newDate = newDate.replace(year, '00'+year)
    elif(len(year) == 3):
        newDate = newDate.replace(year, '0'+year)
    return newDate

def process_date(date):
    newDate = date
    if('bc' in date): 
        newDate = '-'+date.replace('bc', '')
    if('ad' in date):
        newDate = date.replace('ad', '')

    # iif date includes a month
    if(any(month in newDate for month in months)):
        newDate = month_to_num(newDate)
        newDate = to_dd_mm_yyy(newDate)
    
    newDate = datetime.datetime.strptime(newDate, '%m %d %Y').strftime('%Y-%m-%d')

    print(date, ' | ', newDate)

    # isNegative = False
    # if('-' in newDate):
    #     isNegative = True
    #     newDate = newDate.replace('-', '')
    # year = newDate.strip().split(' ')[-1]
    # print(year)
    # print('---')
    # print(year)
 
    # if(isNegative):
    #     newDate = '-'+newDate
    return newDate


def process(df):
    for i, row in df.iterrows():
        row['starteDate'] = process_date(row['startDate'].lower().strip())
    return df


def upload(name, title):
    df = pd.read_csv(name+'.csv', index_col=False)
    df = df.replace({np.nan: None})
    df = process(df)
    print(df)

    # firestore_init.init()
    # db = FirestoreDB()
    # user = auth.get_user_by_email('timelines.contact@gmail.com').__dict__['_data']
    # user['uid'] = user['localId']
    # db.set_user(user)

    # timeline = {'uid': user['uid'], 'name': title, 'isPublic': True, 'lastUsed': int(time.time())}
    # timeline['id'] = db.add("timelines", timeline)
    # for i, row in df.iterrows():
    #     event = {'uid': user['uid'], 'tid': timeline['id'], 'name': row['name'], 'startDate': row['startDate'], 'description': row['description'], 'endDate': row['endDate']}
    #     print(event)
        # db.add('events', event)