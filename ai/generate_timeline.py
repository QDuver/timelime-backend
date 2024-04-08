import json
import numpy as np
import openai
from ai import process, prompts, langchain_client as langchain
import pandas as pd
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain.output_parsers import PydanticOutputParser
from typing import List, Optional

OPEN_API_MODEL = "gpt-3.5-turbo" 
pd.set_option('display.max_columns', None)

def main(timeline_name, n_events, lang='en', image_association = None):

  class Event(BaseModel):
    name: str = Field(description='name of the event')
    startDate: str = Field(description='Start date of the event in YYYY-MM-DD format')
    endDate: Optional[str] = Field(None, description='End date of the event  in YYYY-MM-DD format (optional)')
    description: str = Field(description='Description of the event')

  class EventsList(BaseModel):
    events: List[Event] = Field(description='List of events')

  parser = PydanticOutputParser(pydantic_object=EventsList)
  resp = langchain.prompt_open_ai(prompts.TIMELIME_PROMPT, {'timeline_name': timeline_name, 'n_events': n_events, 'format_instructions': parser.get_format_instructions()})
  events = json.loads(resp.content)['events']
  if(len(events) < 1):
    raise Exception("No events generated")
  events = process_timeline(events)
  return events
  

def process_timeline(events):
    df =pd.DataFrame(events)
    df = df.replace({np.nan: None})
    df = df.astype(str).replace({'none': None}).replace({'None': None})
    df = df.drop_duplicates(subset=['name', 'startDate'], keep='first')
    df = process.process_dates(df)
    return df.to_dict(orient='records')