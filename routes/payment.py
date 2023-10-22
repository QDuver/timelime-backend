
import time
import stripe
from decorators.decorators import error_handler, token_required
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.utils import get_secret
from flask import Blueprint, jsonify, request, current_app as app
import os

payment_bp = Blueprint('payment', __name__)
FE_URL = os.environ.get('FE_URL')

@payment_bp.route('/cancel-premium', endpoint="cancel_premium", methods=['POST'])
@error_handler
@token_required
def cancel_premium():
    dummy = request.json
    db = app.config['db']
    stripe.api_key = get_secret('stripe')
    if(db.user.stripeCustomerId):
        customer = stripe.Customer.retrieve(db.user.stripeCustomerId)
        customer_subscriptions = stripe.Subscription.list(customer=customer.id)
        for subscription in customer_subscriptions:
            stripe.Subscription.delete(subscription.id)
    db.edit('users', db.user.uid, {'isPremium': False, 'lastPaymentFailed': False})
    return jsonify(success=True)

@payment_bp.route('/create-checkout-session', endpoint="checkout", methods=['POST'])
@error_handler
@token_required
def checkout():
    payload = request.json
    stripe.api_key = get_secret('stripe')

    checkout_session = stripe.checkout.Session.create(
        mode='setup',
        payment_method_types=['card'],
        success_url= f'{FE_URL}/{payload["lang"]}/profile?session_id='+ '{CHECKOUT_SESSION_ID}',
        cancel_url=f'{FE_URL}/{payload["lang"]}?cancel-payment=t',
        customer_email=app.config['db'].user.email,
        metadata={'uid': app.config['db'].user.uid}
    )
    return jsonify({'id': checkout_session.id})


@payment_bp.route('/stripe-webhook', endpoint="webhook", methods=['POST'])
def webhook():
    db = UnprotectedFirestoreDB()
    stripe.api_key = get_secret('stripe')
    endpoint_secret = get_secret('stripe-webhook')
    event = stripe.Webhook.construct_event(
         request.data, request.headers['STRIPE_SIGNATURE'], endpoint_secret)

    session_id = event['data']['object']['id']
    if event['type'] == 'checkout.session.completed':
      uid = event['data']['object']['metadata']['uid']
      create_subscription(session_id, uid)
      if uid:
        db.edit('users', uid, {'isPremium': True, 'lastPaymentFailed': False})
        return jsonify(success=True)

    if event['type'] == 'invoice.payment_failed':
      uid = event['data']['object']['subscription_details']['metadata']['uid']
      if uid:
        db.edit('users', uid, {'isPremium': False, 'lastPaymentFailed': True})
        return jsonify(success=True)


    if(event['type'] == 'invoice.payment_succeeded'):
        uid = event['data']['object']['subscription_details']['metadata']['uid']
        if uid:
            db.edit('users', uid, {'isPremium': True, 'lastPaymentFailed': False})
            return jsonify(success=True)

    return jsonify(success=False)


def create_subscription(session_id, uid):
    db = UnprotectedFirestoreDB()
    user = db.get('users', uid)
    if(db.get('stripe_sessions', session_id)):
        return
    db.add('stripe_sessions', {}, doc_id = session_id)
    stripe.api_key = get_secret('stripe')
    prices = stripe.Price.list( expand=['data.product'] )
    session = stripe.checkout.Session.retrieve( session_id )
    setup_intent = stripe.SetupIntent.retrieve( session["setup_intent"] )
    payment_method = setup_intent["payment_method"]
    customer = stripe.Customer.create(description=uid, email=user['email'], metadata={'uid': uid} )
    db.edit('users', uid, {'stripeCustomerId': customer.id})
    stripe.PaymentMethod.attach(payment_method, customer=customer.id)
    stripe.Customer.modify(customer.id, invoice_settings={'default_payment_method': payment_method})
    customer = stripe.Customer.retrieve(customer.id)
    # stripe.Subscription.create( customer=customer.id, items=[ {"price": prices.data[0].id}, ],  metadata={'uid': uid}, )
    stripe.Subscription.create( customer=customer.id, items=[ {"price": prices.data[0].id}, ], trial_period_days=1, metadata={'uid': uid}, )