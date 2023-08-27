import pandas as pd
import ai as ai
from firestore_db import FirestoreDB, firestore_init
from firebase_admin import auth
import time
import datetime
from utils import events as events
import numpy as np

df = pd.read_csv('timeline.csv', index_col=False)
print(df.head())
df = df.replace({np.nan: None})


firestore_init.init()
db = FirestoreDB()
# uid = '12zFicRtnySeH32DOcDRoGQiyPv1'
user = auth.get_user_by_email('quentin.duverge@gmail.com').__dict__['_data']
user['uid'] = user['localId']
db.set_user(user)

title = 'Space exploration'
timeline = {'uid': user['uid'], 'name': title, 'isPublic': True, 'lastUsed': int(time.time())}
timeline['id'] = db.add("timelines", timeline)
for i, row in df.iterrows():
    event = {'uid': user['uid'], 'tid': timeline['id'], 'name': row['events'], 'startDate': row['startDate'], 'description': row['description'], 'endDate': row['endDate']}
    db.add('events', event)