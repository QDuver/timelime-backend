import jwt

audience = 'time-lime'

def encode_token(headers, key):
    

    payload = {
        'aud': audience,  # Audience
        'origin': headers['Origin'],  # Origin
    }


    token = jwt.encode(payload, key, algorithm='HS256')
    return token

def decode_token(token, key):
    audience = jwt.decode(token, key, algorithms=['HS256'], audience=audience)
