import config as c
from google.cloud.firestore import DELETE_FIELD

def main():
    users = c.udb.get('users')
    for user in users:

        if(c.udb.get('quiz_results', doc=user['uid'])):
            continue

        if('quiz_results' in user and len(user['quiz_results']) > 0):
            results = user['quiz_results']
        elif('quizResults' in user and len(user['quizResults']) > 0):
            results = user['quizResults']
        else:
            continue

        results  = {'results': results}
        c.udb.add('quiz_results', results, doc_id=user['uid'])
        c.udb.edit('users', user['id'], {'quiz_results': DELETE_FIELD, 'quizResults': DELETE_FIELD})
        print(results)


