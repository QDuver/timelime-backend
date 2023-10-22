import datetime
import json
import re
import openai
import pandas as pd
from firestore.firestore_db import UnprotectedFirestoreDB
from models.user import User
from routes.timelines import _process_timeline, create_new_timeline
from utils import event_methods

from utils.utils import divide_chunks, get_secret, set_env_variables
set_env_variables()
openai.api_key = get_secret('OpenAPI')
langs = [
    {'name': 'French', 'code': 'fr'},
    {'name': 'Spanish', 'code': 'es'},
    {'name': 'German', 'code': 'de'},
    {'name': 'Italian', 'code': 'it'},
    {'name': 'Portuguese', 'code': 'pt'}
]
def main():

    existing_keys = ['examples']
    try:
        with open('C:/Users/Msi/Desktop/timelime-frontend-2/src/assets/translations/main/translations.json', 'r') as file:
            translations = json.load(file)
        existing_keys = existing_keys + list(translations.keys())
    except FileNotFoundError:
        pass
    
    with open('C:/Users/Msi/Desktop/timelime-frontend-2/src/assets/translations/main/og-translations.json', 'r') as file:
         translations = json.load(file)

    examples = translations['examples']
    keys = list(translations.keys())
    print(keys)
    keys = [key for key in keys if key not in existing_keys]
    print(keys)

    chunks = list(divide_chunks(keys, 2))
    for chunk in chunks:
        print(chunk)
        to_translate = {key: translations[key] for key in chunk}
        system = '''
        You are an experienced translator, and you have been hired to translate a timeline web application.
        You prioritize translations that are relevant in the context of a timeline web application over word for word translations.
        Output should be a JSON with the same structure as the input JSON, so no text before / after the curly brackets.
        '''
        msg = f''' 
        Your task is generate translations for all the empty strings, based on the non-empty strings.
        All english strings are already present and are in the "en" key.
        "pt" key is for Portuguese, "fr" for French, "es" for Spanish, "de" for German, "it" for Italian.
        Some values are already translated, you should leave them as they are, just fill in the empty strings.

        Do not escape any characters.
        Here are some example translations to help you get started :
        {examples}
        And here are the actual texts to translate: 
        {to_translate} 
'''
        
        response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": msg},
            ]
        )

        translated_chunk = response['choices'][0]['message']['content']
        translated_chunk = translated_chunk.replace("{'", '{"').replace("'}", '"}').replace("':", '":').replace("',", '",').replace("'}", '"}').replace("{'", '{"').replace(": '", ': "').replace(", '", ', "').replace("\\", "")
        print(translated_chunk)
        update_translations(json.loads(translated_chunk))

def update_translations(translated):
    try:
        with open('C:/Users/Msi/Desktop/timelime-frontend-2/src/assets/translations/main/translations.json', 'r', encoding='utf-8') as file:
            translations = json.load(file)
        translations.update(translated)
        with open('C:/Users/Msi/Desktop/timelime-frontend-2/src/assets/translations/main/translations.json', 'w', encoding='utf-8') as file:
            json.dump(translations, file)
    except FileNotFoundError:
        with open('C:/Users/Msi/Desktop/timelime-frontend-2/src/assets/translations/main/translations.json', 'w', encoding='utf-8') as file:
           json.dump(translated, file)

def legal():

    sections = ['privacy-policy', 'terms-of-use']
    for section in sections:
        for lang in langs:

            with open(f'C:/Users/Msi/Desktop/timelime-frontend-2/src/assets/translations/legal/{section}/en.html', 'r') as file:
                legal = file.read()

            system = f'''
            Please provide a {lang['name']} translation of the following html document.
            HTML tags should be left as they are.
                    '''
            msg = f''' {legal} '''
            response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": msg},
                ]
            )

            translated = response['choices'][0]['message']['content']
            translated = translated.replace("\\", "")
            with open(f'C:/Users/Msi/Desktop/timelime-frontend-2/src/assets/translations/legal/{section}/{lang["code"]}.html', 'w', encoding='utf-8') as file:
                file.write(translated)

def translate_timeline():
    scientific_discoveries = {
        "tid": "9L4uPocMUPJUtuv797vn",
        "translations": [
            {"timeline_name": "Les Découvertes scientifiques", "lang": "French "},
            {"timeline_name": "Descubrimientos científicos", "lang": "Spanish"},
            {"timeline_name": "Wissenschaftliche Entdeckungen", "lang": "German"},
            {"timeline_name": "Scoperte scientifiche", "lang": "Italian "},
            {"timeline_name": "Descobertas científicas", "lang": "Portuguese"}
        ]
    }

    roman_empire = {
        "tid": "BQLUIloYtTsqBUwKwt8W",
        "translations": [
            {"timeline_name": "L'Empire romain", "lang": "French "},
            {"timeline_name": "El Imperio romano", "lang": "Spanish"},
            {"timeline_name": "Das Römische Reich", "lang": "German"},
            {"timeline_name": "L'Impero romano", "lang": "Italian "},
            {"timeline_name": "O Império Romano", "lang": "Portuguese"}
        ]
    }

    space_exploration = {
        "tid": "bAIsSOGstg4ySzHAKV59",
        "translations": [
            # {"timeline_name": "L'exploration spatiale", "lang": "French "},
            # {"timeline_name": "Exploración espacial", "lang": "Spanish"},
            # {"timeline_name": "Weltraumforschung", "lang": "German"},
            {"timeline_name": "Esplorazione spaziale", "lang": "Italian "},
            {"timeline_name": "Exploração espacial", "lang": "Portuguese"}
        ]
    }

    db = UnprotectedFirestoreDB()
    db.set_user(User(db, uid='0Gu3S71O2Thq0bSv5DTY7pszf1P2'))
    
    events = event_methods.get_events(db, space_exploration["tid"])['events']
    events = pd.DataFrame(events)
    events = events.loc[events['isEndEvent'] != True]
    events = events.loc[events['isStepDate'] != True]
    events = events.reset_index(drop=True)
    for translation in space_exploration['translations']:

        msg = f'''
        Provide a translation of the following json into {translation['lang']}:
        {events[['name', 'description', 'categoryName']].to_json(orient='records')}
        '''
        response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
                {"role": "system", "content": f''' 
                Response should be a json file, without text around.
                '''},
                {"role": "user", "content": msg},
            ]
        )

        resp = response['choices'][0]['message']['content'] 
        df2 = pd.DataFrame(json.loads(resp))
        events = df2.join(events[['startDate', 'endDate', 'imageURL', 'categoryColor']])
        timeline = create_new_timeline(translation["timeline_name"], 'manual')
        timeline = _process_timeline(db, timeline)
        events['tid'] = timeline['id']
        default_events = event_methods.create_events(db, events.to_dict('records'))
        db.add_batch('events', default_events)
        print(translation, timeline['id'])