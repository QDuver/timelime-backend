import openai
import pandas as pd

openai.api_key = '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'

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a historian."},
        {"role": "user", "content": '''
        Generate a historic timeline of Space exploration, with a focus on USSR / USA competition. 
        It has to be in array of dictionnary format with keys: events, description, startDate, endDate. endDate is optional, but make sure you include at least 3 events which contain both startDate and endDate. 
        Dates have to be in either YYYY-MM-DD or YYYY-MM or YYYY format.
        Max 25 events '''},
    ]
)

resp = response['choices'][0]['message']['content']
print(resp)
df = pd.DataFrame(eval(resp))
df.to_csv('timeline.csv', index=False)
