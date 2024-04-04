from openai import OpenAI


def generate_image(prompt):
  client = OpenAI()

  response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
  )

  image_url = response.data[0].url
  print(image_url)
  return image_url
    

    