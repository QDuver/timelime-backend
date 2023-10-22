
from migrations.migrate_db import init_projects, migrate_example_timelines
from translations import translations

# translations.main() 
# delete_all_users()
# clean_schedule('aa')
preprod_db, prod_db = init_projects()
migrate_example_timelines(preprod_db, prod_db, 'KxyRtAYovzTTQhqOgB92')