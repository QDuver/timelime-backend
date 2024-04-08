import ast
import datetime
import re
from config import db
from utils import event_methods as events_utils
from utils.event_methods import validate_dates, process_date, handle_centuries, handle_decades

def process_dates(df):
    if not ('endDate' in df.columns):
      df['endDate'] = None
    df['startDate'] = df['startDate'].apply(lambda x: process_date(x))
    df['endDate'] = df['endDate'].apply(lambda x: process_date(x))
    df  = df.apply(lambda x: handle_centuries(x), axis=1)
    df  = df.apply(lambda x: handle_decades(x), axis=1)
    df = df.apply(lambda x: events_utils.strip_leading_zeros(x), axis=1)
    df['endDate'] = df.apply(validate_dates, axis=1)

    return df



def process_ai_quiz(df):
    df = df.head(10)
    df = df.astype(str).replace({'none': None}).replace({'None': None})
    quiz = {}
    quiz['questions'] = df['question'].tolist()
    quiz['options'] = []
    for i, option  in enumerate(df['options'].tolist()):
        d = {}
        options = ast.literal_eval(option)
        for i, option2 in enumerate(options):
            d[f'q{i}'] = re.sub(r'^[a-zA-Z]\)\s+', '', option2)
        quiz['options'].append(d)
    answer = df['answer'].tolist()
    answer = [re.sub(r'^[a-zA-Z]\)\s+', '', str(a)) for a in answer]
    quiz['answer'] = answer

    quiz['created_on'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    quiz['uid'] = db.uid
        
    return quiz