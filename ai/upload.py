import pandas as pd
from firestore_db import FirestoreDB, firestore_init
from firebase_admin import auth
import time
import datetime
from utils import events as events
import numpy as np


def upload(name, title):
    df = pd.read_csv(name+'.csv', index_col=False)
    df = df.replace({np.nan: None})


    firestore_init.init()
    db = FirestoreDB()
    user = auth.get_user_by_email('timelines.contact@gmail.com').__dict__['_data']
    user['uid'] = user['localId']
    db.set_user(user)

    title = 'Space exploration'
    timeline = {'uid': user['uid'], 'name': title, 'isPublic': True, 'lastUsed': int(time.time())}
    timeline['id'] = db.add("timelines", timeline)
    for i, row in df.iterrows():
        event = {'uid': user['uid'], 'tid': timeline['id'], 'name': row['name'], 'startDate': row['startDate'], 'description': row['description'], 'endDate': row['endDate']}
        db.add('events', event)