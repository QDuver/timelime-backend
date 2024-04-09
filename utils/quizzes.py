


import ast
import datetime
import re
import config as c


def generate_ai_quiz(events, lang='en'):
    pass
    # events = [event for event in events if 'name' in event and 'startDate' in event and event['startDate']]
    # events = [{'name': event['name'], 'startDate': event['startDate'], 'endDate': event['endDate'], 'description': event['description']} for event in events]
    # n_events = len(events) if len(events) < 10 else 10
    # if(n_events < 1):
    #     raise Exception('No events found in the timeline')

    # prompt = prompts.get_quiz_prompts(n_events, events)
    # resp = openai.ChatCompletion.create(
    # # model="gpt-3.5-turbo",
    # model="gpt-4",
    # messages=[
    #       {"role": "system", "content": prompt[lang][0]},
    #       {"role": "user", "content": prompt[lang][1]},
    #   ]
    # )

    # return process.main(resp, 'quizzes', None)

    
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
    quiz['uid'] = c.user.uid
        
    return quiz