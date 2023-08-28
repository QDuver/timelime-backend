

import openai


def generate_image():
    PROMPT = "A vibrant studio photographic representation of Marie Stuart is held in the Tower of London"

    openai.api_key = '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'

    response = openai.Image.create(
        prompt=PROMPT,
        n=1,
        size="512x512",
    )

    print(response["data"][0]["url"])