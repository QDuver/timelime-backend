
import time
from clean_schedule.main import clean_schedule
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
firestore_init.init()
db = UnprotectedFirestoreDB()
from ai import generate_timeline, process_timeline, generate_quiz, process_quiz, reprocess
from utils.utils import print_full_exception
import pandas as pd



# from utils.cleaning_scripts import delete_all_users_timeline
# delete_all_users_timeline('BaxP33wjGCV5iUTKxiPs5b0Bx4c2')
def _process_timeline():
    df = process_timeline.main('jesus')
    print(df)


def _process_quiz():
    process_quiz.main('the-future')

def read_txt_file():
    with open('ai/generated/quizzes/quiz-portugal.txt', 'r') as file:
        data = file.read()

    df = reprocess.main('asdf', data, 'quizzes')
    df.to_csv(f'ai/generated/quizzes/portugal.csv', index=False)
#     print(df)

_process_quiz()