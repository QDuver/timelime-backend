from ai.generate import generate
from ai.upload import upload
from ai.dalle import generate_image


def main():
  name = "game-thrones"
  title = "Game of Thrones"
  # generate(name, title)
  upload(name, title)