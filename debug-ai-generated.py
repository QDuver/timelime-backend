

from ai.reprocess import interpret_response
from utils.utils import read_from_storage, set_env_variables
from ai.generate_timeline import process_ai_timeline
from ai.generate_quiz import process_ai_quiz
import pandas as pd
pd.set_option('display.max_columns', None)
import io 
import firestore.firestore_init as firestore_init


set_env_variables()
firestore_init.init()
type_ = 'timelines'
sessionId = 'spPOG'
blobs = read_from_storage(type_)
blobs = [blob for blob in blobs if sessionId in blob.name]
for i, blob in enumerate(blobs):
    print(i, blob.name)
    file = blob.download_as_string().decode('utf-8')
    if(i==0):
        print(file)
        df = interpret_response(file, type_)
        print(df)
    if(i==1):
        df = pd.read_csv(io.StringIO(file))
        if(type_=='timelines'):
            df2 = process_ai_timeline(df, 'test', False)
        if(type_=='quizzes'):
            df2 = process_ai_quiz(df, 'test')
        print(df2)
    if(i==2):
        df = pd.read_csv(io.StringIO(file))
        print(df)



        
    # if('.txt' in blob.name):
    #     print(file)
    # if('.csv' in blob.name):
    #     df = pd.read_csv(io.StringIO(file))
    #     print(df)


