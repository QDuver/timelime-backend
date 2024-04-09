

import time
from models.exceptions import CustomException
import config as c
from utils import prompts
from utils.events import assign_tid, process_event_date, handle_centuries, handle_decades, validate_dates, strip_leading_zeros
import json
import numpy as np
from clients import langchain as langchain
import pandas as pd

from utils.parsing import parse_json
pd.set_option('display.max_columns', None)
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from typing import List, Optional
from utils.events import validate_dates, handle_centuries, handle_decades

def create_new_timeline(name, source):
    timeline = {'uid': c.user.uid, 'name': name, 'isPublic': False, 'lastUsed': int(time.time()), 'source': source}
    timeline['id'] = c.db.add("timelines", timeline)
    return timeline


def check_timeline_accessibility(timeline):
    if(not timeline):
        raise CustomException('backend.timelineNotFound')
    timeline['isEditable'] = True
    if(c.user.uid != timeline['uid']):
        if(c.user.isAnonymous and len(timeline['uid']) < 12):
            raise CustomException('backend.timelineExpired')
        if(not timeline['isPublic']):
            raise CustomException('backend.timelinePrivate')
        else:
            timeline['isEditable'] = False
    
    return timeline


def update_timeline(timeline):
    timeline['lastUsed'] = int(time.time())
    c.db.edit("timelines", timeline.id, timeline)
    return timeline



def generate_timeline_name():
    n_timelines = len(c.db.get("timelines", where=('uid', '==', c.user.uid)))
    name = 'My new timeline' if n_timelines == 0 else f'My new timeline ({n_timelines + 1})'
    return name


def generate_ai_timeline(timelineName, nEvents, lang):
    events = generate_ai_events(timelineName, nEvents, lang)
    events = process_ai_events(events)
    timeline = create_new_timeline(timelineName, 'ai')
    events = assign_tid(events, timeline)
    c.db.add_batch('events', events)
    return timeline


def generate_ai_events(timeline_name, n_events, lang='en'):

  class Event(BaseModel):
    name: str = Field(description='name of the event')
    startDate: str = Field(description='Start date of the event in YYYY-MM-DD format')
    endDate: Optional[str] = Field(None, description='End date of the event  in YYYY-MM-DD format (optional)')
    description: str = Field(description='Description of the event')

  class EventsList(BaseModel):
    events: List[Event] = Field(description='List of events')

  parser = PydanticOutputParser(pydantic_object=EventsList)
  resp = langchain.prompt_open_ai(prompts.TIMELIME_PROMPT, {'timeline_name': timeline_name, 'n_events': n_events, 'format_instructions': parser.get_format_instructions()})
  print(resp.content)
  events = parse_json(resp.content)['events']
  if(len(events) < 1):
    raise Exception("No events generated")
  return events
  

def process_ai_events(events):
    df =pd.DataFrame(events)
    df = df.replace({np.nan: None})
    df = df.astype(str).replace({'none': None}).replace({'None': None})
    df = df.drop_duplicates(subset=['name', 'startDate'], keep='first')
    df = process_ai_events_dates(df)
    return df.to_dict(orient='records')

def process_ai_events_dates(df):
    if not ('endDate' in df.columns):
      df['endDate'] = None
    df['startDate'] = df['startDate'].apply(lambda x: process_event_date(x))
    df['endDate'] = df['endDate'].apply(lambda x: process_event_date(x))
    df  = df.apply(lambda x: handle_centuries(x), axis=1)
    df  = df.apply(lambda x: handle_decades(x), axis=1)
    df = df.apply(lambda x: strip_leading_zeros(x), axis=1)
    df['endDate'] = df.apply(validate_dates, axis=1)
    return df