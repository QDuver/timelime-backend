import config as c
from google.cloud.firestore import DELETE_FIELD

def main():
    users = c.udb.get('users')
    for user in users:
        c.udb.edit('users', user['id'], {'generating': DELETE_FIELD})


