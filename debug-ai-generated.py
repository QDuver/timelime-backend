

from ai.process import interpret_response, process_ai_timeline, process_ai_quiz
from utils.utils import read_from_storage, set_env_variables
import pandas as pd
pd.set_option('display.max_columns', None)
import io 
import firestore.firestore_init as firestore_init


set_env_variables()
firestore_init.init()
type_ = 'quizzes'
sessionId = 'mPBkO'
blobs = read_from_storage(type_)
blobs = [blob for blob in blobs if sessionId in blob.name]
for i, blob in enumerate(blobs):
    print(i, blob.name)
    file = blob.download_as_string().decode('utf-8')
    if('step1' in blob.name or 'step2' in blob.name):
        print(file)
        df = interpret_response(file)
        print(df)
    if('step3' in blob.name):
        df = pd.read_csv(io.StringIO(file))
        if(type_=='timelines'):
            df2 = process_ai_timeline(df, 'test', False)
        if(type_=='quizzes'):
            df2 = process_ai_quiz(df, 'test')
        print(df2)
    if('step4' in blob.name):
        df = pd.read_csv(io.StringIO(file))
        print(df)


