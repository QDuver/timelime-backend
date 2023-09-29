

import stripe
from clean_schedule.main import UnprotectedFirestoreDB
from utils.utils import get_secret, set_env_variables
import firestore.firestore_init as firestore_init

set_env_variables()
firestore_init.init()
stripe.api_key = get_secret('stripe')
session_id = "cs_test_c13ymui8a8y5tP8pKhOzDnhH8Lx95wTU0NiJ9V6KGvsKzqjp8OpIyKHJQk"
uid = 'KPsZI1k1XiVKDC0wmGh1HnF3D8u1'
db = UnprotectedFirestoreDB()
user = db.get('users', uid)

prices = stripe.Price.list( expand=['data.product'] )
session = stripe.checkout.Session.retrieve( session_id )
setup_intent = stripe.SetupIntent.retrieve( session["setup_intent"] )
payment_method = setup_intent["payment_method"]
stripe.PaymentMethod.attach(payment_method, customer='cus_Oj7VtYI1sX36qC')
# customer = stripe.Customer.create(description=uid, email=user['email'], metadata={'uid': uid})
# stripe.Subscription.create( customer=customer.id, items=[ {"price": prices.data[0].id}, ], trial_period_days=1, metadata={'uid': uid}, )
customer = stripe.Customer.retrieve('cus_Oj7VtYI1sX36qC')
print(customer)
# stripe.Subscription.create( customer=customer.id, items=[ {"price": prices.data[0].id}, ],  metadata={'uid': uid}, )
