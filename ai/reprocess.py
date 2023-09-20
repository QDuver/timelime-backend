import openai
import pandas as pd
import time

from utils.utils import get_secret, save_df_to_storage, save_text_to_storage

def main(name, text, type_):

    if(type_ == 'quizzes'):
        format_ = '{question: string, options: string[], answer: string}'
    elif(type_ == 'timelines'):
        format_ = '{name, description, startDate, endDate}'

    openai.api_key = get_secret('OpenAPI')

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k-0613",
    messages=[
            {"role": "system", "content": f'''
            Response should be a JSON object with the following format: [{format_}, {format_}, ...]
            '''},
            {"role": "user", "content": f'''
            Reprocess the following text so that the response is readable by pandas.read_json without any errors.
            Only provide the response, not other text : 
            {text}
                '''},
        ]
    )

    resp = response['choices'][0]['message']['content']
    try: 
        df = pd.read_json(resp)
        return df
    except:
        try:
            obj = eval(resp)
            df = pd.read_json(obj)
            return df
        except:
            try:
                obj = eval(resp)
                obj = obj[list(obj.keys())[0]]
                df = pd.DataFrame(obj)
                return df
            except:
                save_text_to_storage(resp, f'ai-generated/timelines/{name}')
                raise Exception('Could not parse response')


