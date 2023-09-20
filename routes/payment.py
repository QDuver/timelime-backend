import json
import os
import stripe
from decorators.decorators import generic_error_handler, token_required
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.utils import get_fe_url, get_secret, print_full_exception
from flask import Blueprint, jsonify, request, current_app as app

stripe.api_key = get_secret('stripe')
payment_bp = Blueprint('payment', __name__)
FE_URL = get_fe_url()

@payment_bp.route('/cancel-premium', endpoint="simple", methods=['POST'])
@generic_error_handler
@token_required
def cancel_premium():
    db = app.config['db']
    db.edit('users', db.user.uid, {'isPremium': False})
    return jsonify(success=True)


@payment_bp.route('/create-checkout-session', endpoint="checkout", methods=['POST'])
@generic_error_handler
@token_required
def checkout():
    print('stripe general endpoint_secret', get_secret('stripe'), flush=True)
    dummy = request.json
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
# @generic_error_handler
def webhook():
    endpoint_secret = get_secret('stripe-webhook')
    print('webhook endpoint_secret', endpoint_secret, flush=True)
    event = stripe.Webhook.construct_event(
         request.data, request.headers['STRIPE_SIGNATURE'], endpoint_secret)

    if event['type'] == 'checkout.session.completed':
      uid = event['data']['object']['metadata']['uid']
      print('UID', uid, flush=True)
      if uid:
        db = UnprotectedFirestoreDB()
        db.edit('users', uid, {'isPremium': True})
        return jsonify(success=True)


    return jsonify(success=False)