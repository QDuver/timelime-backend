
import firestore.firestore_init as firestore_init
firestore_init.init()

from ai import upload, generate
name = 'space-exploration'
title = 'Space Exploration, with a focus on USSR / USA competition'
generate.generate(name, title)
upload.upload(name, title)

# import utils.cleaning_scripts as cleaning_scripts
# cleaning_scripts.delete_all_first_timelines()