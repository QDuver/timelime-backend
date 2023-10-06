
import time
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from migrations.migrate_db import change_timeline_uid, init_projects, migrate_example_quizzes
from utils.cleaning_scripts import delete_all_users_timeline
from utils.utils import set_env_variables
from utils.event_methods import strip_leading_zeros
from ai import tests

# tests.main()
delete_all_users_timeline('0Gu3S71O2Thq0bSv5DTY7pszf1P2')