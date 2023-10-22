
import time
from clean_schedule.main import clean_schedule
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from migrations.migrate_db import change_timeline_uid, init_projects, migrate_example_quizzes
from utils.cleaning_scripts import delete_all_first_timelines, delete_all_users, delete_all_users_timeline
from utils.utils import set_env_variables
from utils.event_methods import strip_leading_zeros
from ai import tests
from translations import translations

# translations.main()
# delete_all_users()
clean_schedule('aa')