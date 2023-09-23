
import stripe
from decorators.decorators import generic_error_handler, token_required
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.utils import get_secret
from flask import Blueprint, jsonify, request, current_app as app
import os

payment_bp = Blueprint('payment', __name__)
FE_URL = os.environ.get('FE_URL')

@payment_bp.route('/cancel-premium', endpoint="simple", methods=['POST'])
@generic_error_handler
@token_required
def cancel_premium():
    db = app.config['db']
    stripe.api_key = get_secret('stripe')
    stripe.Subscription.cancel(db.user.subscription)
    db.edit('users', db.user.uid, {'isPremium': False, 'subscription': None})
    return jsonify(success=True)


@payment_bp.route('/create-checkout-session', endpoint="checkout", methods=['POST'])
@generic_error_handler
@token_required
def checkout():
    dummy = request.json
    stripe.api_key = get_secret('stripe')
    prices = stripe.Price.list(
    expand=['data.product']
)
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                'price': prices.data[0].id,
                'quantity': 1,
            },
        ],
        mode='subscription',
        success_url=FE_URL +
        '/#/profile?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=FE_URL + '/#?cancel-payment=t',
        customer_email=app.config['db'].user.email,
        metadata={'uid': app.config['db'].user.uid}
    )
    return jsonify({'id': checkout_session.id})

@payment_bp.route('/stripe-webhook', endpoint="webhook", methods=['POST'])
def webhook():
    stripe.api_key = get_secret('stripe')
    endpoint_secret = get_secret('stripe-webhook')
    event = stripe.Webhook.construct_event(
         request.data, request.headers['STRIPE_SIGNATURE'], endpoint_secret)

    if event['type'] == 'checkout.session.completed':
      uid = event['data']['object']['metadata']['uid']
      if uid:
        db = UnprotectedFirestoreDB()
        db.edit('users', uid, {'isPremium': True, 'subscription': event['data']['object']['subscription']})
        return jsonify(success=True)


    return jsonify(success=False)
