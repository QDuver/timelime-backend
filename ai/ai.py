from ai.generate import generate
from ai.upload import upload
from ai.dalle import generate_image


def main(name, title):
  generate(name, title)
  upload(name, title)