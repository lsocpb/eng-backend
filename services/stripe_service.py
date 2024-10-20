import json
import uuid

import stripe
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException

import repos.user_repo
from utils.constants import DOMAIN_BASE, TransactionStatus, STRIPE_LISTENING_EVENTS, STRIPE_PAYMENT_SUCCESS_URL, \
    STRIPE_PAYMENT_CANCEL_URL


def create_payment_url(session: Session, amount: float, user_id: str):
    user = repos.user_repo.get_by_id(session, int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    transaction_uuid = str(uuid.uuid4())

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
        success_url=STRIPE_PAYMENT_SUCCESS_URL,
        cancel_url=STRIPE_PAYMENT_CANCEL_URL,
        automatic_tax={'enabled': False},
        metadata={'transaction_uuid': transaction_uuid},
        payment_intent_data={
            'metadata': {
                'transaction_uuid': transaction_uuid
            }
        }
    )

    repos.user_repo.create_wallet_transaction(session, user, amount, uuid=transaction_uuid,
                                              checkout_session_id=checkout_session.id)

    return checkout_session.url


def stripe_payment_webhook(session: Session, raw_data: str):
    try:
        event = stripe.Event.construct_from(
            json.loads(raw_data), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload from Stripe" + str(e))

    # Log all events for debugging purposes
    with open('webhook_event.json', 'a') as f:
        f.write(json.dumps(event, separators=(',', ':')) + '\n')

    if event['type'] not in STRIPE_LISTENING_EVENTS:
        print(f"Stripe WEBHOOK: Event type {event.type} not supported")
        return

    # Get transaction_uuid from metadata
    if not event.data.object['metadata']:
        raise HTTPException(status_code=400, detail="No metadata found")
    if not event.data.object['metadata']['transaction_uuid']:
        raise HTTPException(status_code=400, detail="No transaction_uuid found")

    transaction_uuid = event.data.object['metadata']['transaction_uuid']
    transaction = repos.user_repo.get_wallet_transaction_by_uuid(session, transaction_uuid)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Handle the event
    print(f"Stripe WEBHOOK: Received event: id={event.id}, type={event.type}")

    if event.type == 'payment_intent.created':
        print(f"Transaction uuid: {transaction_uuid} - Payment intent created")
        transaction.stripe_payment_intent_id = event.data.object['id']
    elif event.type == 'charge.succeeded':
        print(f"Transaction uuid: {transaction_uuid} - Charge succeeded")
        transaction.receipt_url = event.data.object['receipt_url']
    elif event.type == 'payment_intent.succeeded':
        print(f"Transaction uuid: {transaction_uuid} - Payment intent succeeded")
        transaction.transaction_status = TransactionStatus.SUCCESS
        transaction.user.balance_total += transaction.amount
        # todo: send email to user
    elif event.type == 'checkout.session.expired':
        print(f"Transaction uuid: {transaction_uuid} - Checkout session expired")
        transaction.transaction_status = TransactionStatus.EXPIRED

    session.commit()
