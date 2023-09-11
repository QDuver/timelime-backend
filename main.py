
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
firestore_init.init()
db = UnprotectedFirestoreDB()
from ai import generate_timeline, process_timeline, generate_quiz, process_quiz
from utils.utils import print_full_exception


# timelineNames = ['napoleon', 'fencing', 'cinema', 'the life of sigourney weaver', 'basketball', 'clothing', 'the internet', 'the rendez-vous"']
# for timelineName in timelineNames:
#     print(timelineName)
#     try:
#         generate_timeline.main(timelineName, 30)
#         events = process_timeline.generate_events(timelineName, 'noimage')
#         generate_quiz.main(timelineName, events)
#         process_quiz.main(timelineName)
#     except Exception as e:
#         print('Error: ' + timelineName)
#         print_full_exception(e)

timelineName = 'Star Wars Universe'
events = db.get('events', where=('tid', '==', 'ebtJw1QttkF87UwTFouF'))
generate_quiz.main(timelineName, events)
process_quiz.main(timelineName)
# from utils.cleaning_scripts import delete_all_users_timeline
# delete_all_users_timeline('BaxP33wjGCV5iUTKxiPs5b0Bx4c2')