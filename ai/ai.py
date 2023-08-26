import openai

openai.api_key = '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'

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": '''
        Generate a timeline of Henry VIII. 
        It has to be in JSON format with keys: title, description, startDate, endDate. endDate is optional. 
        Dates have to be in either YYYY-MM-DD or YYYY-MM or YYYY format.
        Max 20 events '''},
    ]
)

print(response['choices'][0]['message']['content'])