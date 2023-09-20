import pandas as pd
from firestore.firestore_db import UnprotectedFirestoreDB
from firebase_admin import auth
import time
from datetime import datetime
from utils import methods as events_utils
import numpy as np
import re
from flask import current_app as app
import time

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

def process_negative_literals(date):
    newDate = re.sub(r'[a-zA-Z]', '', date).strip()
    if('-' not in newDate):
        newDate = '-'+newDate
    return newDate

def process_date(date):
    if(date == None): return None
    newDate = date.lower().strip()
    newDate = newDate.replace(', ', '')
    newDate = newDate.replace(',', '')
    if('ac' in newDate): 
        newDate = process_negative_literals(newDate)
    if('bce' in newDate):
        newDate = process_negative_literals(newDate)
    if('bc' in newDate): 
        newDate = process_negative_literals(newDate)
    if('bby' in newDate):
        newDate = process_negative_literals(newDate)
    if('ad' in newDate):
        newDate = newDate.replace('ad', '')
    if('aby' in newDate):
        newDate = newDate.replace('aby', '')

    if(any(month in newDate for month in months)):
        newDate = month_to_num(newDate)
    
    if(newDate == 'present' or newDate == 'ongoing' ):
        newDate = datetime.now().year

    return str(newDate).strip()


def handle_centuries(event):
    if('century' in event['startDate']):
        event['startDate'] = re.search(r'\d+', event['startDate']).group() + '00'
        event['endDate'] = str(int(event['startDate']) + 100)
    return event

def handle_decades(event):
    if('s' in event['startDate']):
        event['startDate'] = re.search(r'\d+', event['startDate']).group()
        event['endDate'] = str(int(event['startDate']) + 10)
    return event

def process(df):
    df['startDate'] = df['startDate'].apply(lambda x: process_date(x))
    df['endDate'] = df['endDate'].apply(lambda x: process_date(x))
    df  = df.apply(lambda x: handle_centuries(x), axis=1)
    df  = df.apply(lambda x: handle_decades(x), axis=1)
    df = df.apply(lambda x: events_utils.strip_leading_zeros(x), axis=1)
    return df


def vaildate_date(date):
    if(date == None): return
    split_date = events_utils.split_date(date)
    if(split_date['year'] < -4600000000 or split_date['year'] > 4600000000):
        raise Exception('year is out of range')

def validate_dates(startDate, endDate):
    if(startDate == None or endDate == None): 
        return endDate
    start_date = events_utils.split_date(startDate)
    end_date = events_utils.split_date(endDate)
    if(start_date['year'] >= end_date['year']):
        return None
    try:
        if(start_date['year'] == end_date['year'] and start_date['month'] > end_date['month']):
            return None
    except KeyError:
        pass
    try:
        if(start_date['year'] == end_date['year'] and start_date['month'] == end_date['month'] and start_date['day'] > end_date['day']):
            return None
    except KeyError:
        pass

def main(df, timelineName, image_association = None):
    try:
        db = app.config['db']
    except:
        db = UnprotectedFirestoreDB()
    
    df = df.replace({np.nan: None})
    df = df.drop_duplicates(subset=['name', 'startDate'], keep='first')
    if not ('endDate' in df.columns):
        df['endDate'] = None
    df = process(df)

    events = []
    for i, row in df.iterrows():
        try:
            vaildate_date(row['startDate'])
            vaildate_date(row['endDate'])
            row['endDate'] = validate_dates(row['startDate'], row['endDate'])
            event = {'uid': db.uid, 'name': row['name'], 'startDate': row['startDate'], 'description': row['description'], 'endDate': row['endDate']}
            if(image_association == 'google'):
                event['imageURL'] = events_utils.get_google_images(row['name'], timelineName)[0]
            events.append(event)
        except Exception as e:
            print('error', e, 'could not load event', row.to_dict())
    
    return events