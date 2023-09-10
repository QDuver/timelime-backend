
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.events import split_date, date_to_days, get_events
firestore_init.init()
db = UnprotectedFirestoreDB()
import os
from ai import generate_timeline, process_timeline, generate_quiz
from utils.cleaning_scripts import delete_all_users_timeline
import pandas as pd
import json
# timeline = db.get('timelines', '8gcTkHXcPZfAjIjD0itI')
# process_timeline.generate_events(timeline, 'henry-viii')

# generate_quiz.main('8gcTkHXcPZfAjIjD0itI')
# upload_quiz.main('BQLUIloYtTsqBUwKwt8W')

# delete_all_users_timeline('BaxP33wjGCV5iUTKxiPs5b0Bx4c2')
# generate_timeline.main('Football', 5)

# read txt file
# with open('ai/generated/fencing.txt', 'r') as f:
#     resp = f.read()
#     resp = resp.replace("{\"", "{'").replace("\": \"", "': '").replace("\", \"", "', '").replace("\"}", "'}")
#     print(resp)
#     obj = eval(resp)
#     if(type(obj) == dict):
#       obj = obj[list(obj.keys())[0]]
#     df = pd.DataFrame(obj)
#     print(df)