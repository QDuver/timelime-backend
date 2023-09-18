import json
import os
import stripe
from decorators.decorators import generic_error_handler, token_required
from utils.utils import get_secret, print_full_exception
from flask import Blueprint, jsonify, request, current_app as app

stripe.api_key = get_secret('stripe-test')
payment_bp = Blueprint('payment', __name__)
YOUR_DOMAIN = 'http://localhost:4200'
endpoint_secret = 'whsec_sU0WQCpTJfVKgzz6jzh4jOKZjZXMQKIt'

@payment_bp.route('/create-checkout-session', endpoint="simple", methods=['POST'])
@generic_error_handler
@token_required
def simple():
    dummy = request.json
    prices = stripe.Price.list(
    lookup_keys=['timelime-premium'],
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
        success_url=YOUR_DOMAIN +
        '/payment-success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=YOUR_DOMAIN + '/#?cancel-payment=t',
        customer_email=app.config['db'].user.email,
        client_reference_id=app.config['db'].user.uid,

    )
    return jsonify({'id': checkout_session.id})

@payment_bp.route('/stripe-webhook', endpoint="webhook", methods=['POST'])
@generic_error_handler
def webhook():
    print(request.data, flush=True)
    event = stripe.Webhook.construct_event(
         request.data, request.headers['STRIPE_SIGNATURE'], endpoint_secret)

    if event['type'] == 'payment_intent.succeeded':
      payment_intent = event['data']['object']
      uid = payment_intent.metadata.get('uid', None)
      if uid:
        app.config['db'].user.update_premium_status(True)
        return jsonify(success=True)


    return jsonify(success=False)