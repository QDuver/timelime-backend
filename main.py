
import time
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from migrations.migrate_db import change_timeline_uid, init_projects, migrate_example_quizzes
from utils.utils import set_env_variables
from utils.event_methods import strip_leading_zeros
from ai import tests

tests.main()