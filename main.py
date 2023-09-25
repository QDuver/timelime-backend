
import time
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from migrations.migrate_db import change_timeline_uid, init_projects, migrate_example_quizzes
from utils.utils import set_env_variables
set_env_variables()
# firestore_init.init()
# db = UnprotectedFirestoreDB()


# delete_all_users_timeline('BaxP33wjGCV5iUTKxiPs5b0Bx4c2')

migrate_example_quizzes()