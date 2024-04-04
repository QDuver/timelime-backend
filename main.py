
from ai import langchain_client
from utils.utils import set_env_variables
from firestore import firestore_init
set_env_variables()
firestore_init.init()
import config
import utils
config.init()
from config import db


event = db.get('events', where= ('tid', '==', 'lYSxp2HDrJO03m4EwVKc'))[0]
utils.image_methods.generate_image('google', event)
print('COUCOU')

# langchain_client.generate_image("Create an image of a halloween night at a haunted museum")