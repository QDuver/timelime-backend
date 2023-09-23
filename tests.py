
import datetime


print(datetime.datetime.now().timestamp())
# get timestamp up to seconds
print(int(datetime.datetime.now().replace(microsecond=0).timestamp()))
