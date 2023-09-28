

import stripe
from utils.utils import get_secret, set_env_variables

set_env_variables()
stripe.api_key = get_secret('stripe')

session = stripe.checkout.Session.retrieve(
    "cs_test_c1RBNz0u9gtB0GDu55VZMn0l5ApEuNCPGF9b7XJbNz1dl7qMEi4yWRzeAd"
)

print(session["setup_intent"])
setup_intent = stripe.SetupIntent.retrieve(
    session["setup_intent"]
)
payment_method = setup_intent["payment_method"]
customer = stripe.Customer.create(
description="My First Test Customer (created for API docs at https://www.stripe.com/docs/api)",
email='quentin.duverge@gmail.com',
metadata={'uid': '123'},
payment_method=payment_method
)
subscription = stripe.Subscription.create(
customer=customer.id,
items=[
    {"price": "price_1NvGxtLwxNX8eOtXeJPEPeWa"},
],
trial_period_days=1,
metadata={'uid': '123'}
    )

# invoice = stripe.Invoice.retrieve(subscription.latest_invoice)
# payment_intent = stripe.PaymentIntent.retrieve(invoice.payment_intent)

# if payment_intent.status == 'requires_action':
#     invoice_url = invoice.hosted_invoice_url