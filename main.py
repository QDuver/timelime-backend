
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.events import split_date, date_to_days, get_events
firestore_init.init()
db = UnprotectedFirestoreDB()
import os
from ai import generate_quiz, upload_quiz, upload_timeline

timeline = db.get('timelines', 'DM0eAFajelFwxXCZnajK')
upload_timeline.main(timeline, 'henry-viii')

# generate_quiz.main('9L4uPocMUPJUtuv797vn')
# upload_quiz.main('BQLUIloYtTsqBUwKwt8W')

# import utils.cleaning_scripts as cleaning_scripts
# cleaning_scripts.delete_all('users')