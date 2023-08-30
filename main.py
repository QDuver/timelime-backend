
import firestore.firestore_init as firestore_init
firestore_init.init()

from ai import upload, generate
name = 'roman-empire'
title = 'The Roman Empire'
# generate.generate(name, title)
upload.upload(name, title)

# import utils.cleaning_scripts as cleaning_scripts
# cleaning_scripts.delete_all_first_timelines()