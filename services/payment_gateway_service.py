import json

import stripe
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException

import repos.user_repo
from utils.constants import DOMAIN_BASE


def create_payment_url(session: Session, amount: float, user_id: str):
    user = repos.user_repo.get_by_id(session, int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                'price_data': {
                    'currency': 'pln',
                    'product_data': {
                        'name': 'Doładowanie portfela CharFair',
                    },
                    'unit_amount': int(amount * 100)
                },
                'quantity': 1
            }
        ],
        mode='payment',
        success_url=DOMAIN_BASE + '/success.html',
        cancel_url=DOMAIN_BASE + '/cancel.html',
        automatic_tax={'enabled': False},
        metadata={'user_id': user_id}
    )
    stripe_payment_id = checkout_session.id

    with open('payment_session.json', 'w') as f:
        f.write(json.dumps(checkout_session, separators=(',', ':')))
    repos.user_repo.create_wallet_transaction(session, user, amount, stripe_payment_id)

    return {"payment_url": checkout_session.url}


def stripe_payment_webhook(session: Session, raw_data: str):
    try:
        event = stripe.Event.construct_from(
            json.loads(raw_data), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload from Stripe" + str(e))

    with open('webhook_event.json', 'w') as f:
        f.write(json.dumps(event, separators=(',', ':')))
    def get_wallet_transaction(sess: Session, stripe_payment_id: str):
        transaction = repos.user_repo.get_wallet_transaction_by_stripe_payment_id(sess, stripe_payment_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return transaction

    # Handle the event
    if event.type == 'checkout.session.completed':
        print('Payment was successful.' + json.dumps(event.data.object))
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        metadata = payment_intent['metadata']
        if not metadata:
            print('No metadata found')
            return
        user_id = metadata['user_id']

        user = repos.user_repo.get_by_id(session, user_id)
        if user is None:
            # minify this error
            minify_json = json.dumps({"message": "User not found"})
            raise HTTPException(status_code=404, detail="User not found")

    elif event.type == 'charge.succeeded':
        wallet_transaction = get_wallet_transaction(session, event.data.object['payment_intent'])
    else:
        print('Unhandled event type {}'.format(event.type))

    print("event type: " + event.type + " | " + json.dumps(event.data.object, separators=(',', ':')))
