
import firestore.firestore_init as firestore_init
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.events import split_date, date_to_days, get_events
firestore_init.init()
db = UnprotectedFirestoreDB()


    # print(event['previousEventDistance'])

# from ai import upload, generate
# name = 'year 2022'
# title = 'of year 2022'
# generate.generate(name, title)
# upload.upload(name, title)

# import utils.cleaning_scripts as cleaning_scripts
# cleaning_scripts.delete_all('users')