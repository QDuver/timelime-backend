import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config as c
from migrations import remove_generating_from_users, dedicated_coll_for_quiz_results


def run_migrations():
    c.init_firebase()
    c.init_udb()
    remove_generating_from_users.main()
    dedicated_coll_for_quiz_results.main()

run_migrations()