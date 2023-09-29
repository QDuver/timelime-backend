

import stripe
from clean_schedule.main import UnprotectedFirestoreDB
from utils.utils import get_secret, set_env_variables
import firestore.firestore_init as firestore_init

set_env_variables()
firestore_init.init()
stripe.api_key = get_secret('stripe')
session_id = "cs_test_c13ymui8a8y5tP8pKhOzDnhH8Lx95wTU0NiJ9V6KGvsKzqjp8OpIyKHJQk"
uid = '	0Gu3S71O2Thq0bSv5DTY7pszf1P2'
db = UnprotectedFirestoreDB()
user = db.get('users', uid)

# find stripe customer by metadata uid
customer = stripe.Customer.retrieve(user['stripeCustomerId'])
print(customer)