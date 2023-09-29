import openai
from utils.utils import get_secret, set_env_variables

set_env_variables()
openai.api_key = get_secret('OpenAPI')

msg = '''
With this code :
    stripe.api_key = get_secret('stripe')
    prices = stripe.Price.list( expand=['data.product'] )
    session = stripe.checkout.Session.retrieve( session_id )
    setup_intent = stripe.SetupIntent.retrieve( session["setup_intent"] )
    payment_method = setup_intent["payment_method"]
    customer = stripe.Customer.create(description=uid, email=user['email'], metadata={'uid': uid} )
    stripe.PaymentMethod.attach(payment_method, customer=customer.id)
    customer = stripe.Customer.retrieve(customer.id)
    stripe.Subscription.create( customer=customer.id, items=[ {"price": prices.data[0].id}, ],  metadata={'uid': uid}, )

    I still get this error : 
    This customer has no attached payment source or default payment method.
'''

response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
        {"role": "system", "content": f''' '''},
        {"role": "user", "content": msg},
    ]
)

print(response['choices'][0]['message']['content'])




        