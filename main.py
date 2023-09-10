
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.events import split_date, date_to_days, get_events
firestore_init.init()
db = UnprotectedFirestoreDB()
import os
from ai import generate_timeline, process_timeline, generate_quiz
from utils.cleaning_scripts import delete_all_users_timeline

# timeline = db.get('timelines', '8gcTkHXcPZfAjIjD0itI')
# process_timeline.generate_events(timeline, 'henry-viii')

# generate_quiz.main('8gcTkHXcPZfAjIjD0itI')
# upload_quiz.main('BQLUIloYtTsqBUwKwt8W')

delete_all_users_timeline('BaxP33wjGCV5iUTKxiPs5b0Bx4c2')
# generate_timeline.main('Football', 5)


# time to generate 10 events 8.106298446655273
# time to generate 50 events 26.873568058013916
# time to generate 35 events 55.60773205757141
# time to generate 35 events 22.010106325149536
# time to generate 10 events 13.579435586929321
# time to generate 4 events 3.635265588760376

# finished generatin quiz for 22 events -16.009074211120605
# finished generatin quiz for 10 events -19.894840002059937