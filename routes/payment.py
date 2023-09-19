import json
import os
import stripe
from decorators.decorators import generic_error_handler, token_required
from firestore.firestore_db import UnprotectedFirestoreDB
from utils.utils import get_secret, print_full_exception
from flask import Blueprint, jsonify, request, current_app as app

stripe.api_key = 'sk_test_51NrQJzLwxNX8eOtXEBGd8yONGcPQ50DswyrdhEqjdfN1S3oJSyoLiwWHr29WfBMvaby7lTCCH4LfV1F0aqrqmE2T00Q3crmVPR'
# stripe.api_key = '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'
payment_bp = Blueprint('payment', __name__)
YOUR_DOMAIN = 'http://localhost:4200'

# 

@payment_bp.route('/create-checkout-session', endpoint="simple", methods=['POST'])
@generic_error_handler
@token_required
def simple():
    dummy = request.json
    prices = stripe.Price.list(
    expand=['data.product']
)
    print(prices, flush=True)
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
        metadata={'uid': app.config['db'].user.uid}
    )
    return jsonify({'id': checkout_session.id})

@payment_bp.route('/stripe-webhook', endpoint="webhook", methods=['POST'])
# @generic_error_handler
def webhook():
    endpoint_secret = 'whsec_EDBhrbf7wUw56lGmB28yup6ZAR8e9jwX'
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