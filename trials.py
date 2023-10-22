import json

test = '''
[{"name":null,"description":"","categoryName":""}]
'''
evaluation = json.loads(test)
print(evaluation)
#evaluation returns null