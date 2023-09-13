import openai
from utils.utils import get_secret

def generate_image(prompt):
    prompt = f'A vibrant studio photographic representation of {prompt}'
    openai.api_key = get_secret('OpenAPI')
    response = openai.Image.create( prompt=prompt, n=1, size='512x512')
    print(response["data"][0]["url"])
    

    