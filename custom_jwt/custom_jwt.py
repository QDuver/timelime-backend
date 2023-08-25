import jwt

audience = 'time-lime'

def encode_token(headers, key): 
    return jwt.encode({ 'aud': audience, 'origin': headers['Origin'], }, key, algorithm='HS256')

def decode_token(token, key):
    decoded = jwt.decode(token, key, algorithms=['HS256'], audience=audience)
    if(decoded['aud'] != audience):
        raise Exception('Invalid audience')
    if 'localhost' not in decoded['origin'] and 'time-lime' not in decoded['origin'] and 'timelime' not in decoded['origin']: 
        raise Exception('Invalid origin')
