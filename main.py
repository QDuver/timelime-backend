
from ai import langchain_client
from utils.utils import set_env_variables
from firestore import firestore_init
set_env_variables()
firestore_init.init()
from firestore.firestore_db import UsedDB, db
from utils.image_methods import generate_image

event = db.get('events', where= ('tid', '==', 'lYSxp2HDrJO03m4EwVKc'))[0]

generate_image('ai', event)