from jinja2 import Template
from sendgrid import Mail, SendGridAPIClient

from controllers.user_controller import SENDGRID_FROM_EMAIL, SENDGRID_API_KEY
from db_management.models import User, Auction
from utils.constants import fastapi_logger as logger

with open("templates/auction_won.html", "r", encoding='utf-8') as file:
    auction_won_template = file.read()

with open("templates/auction_completed.html", "r", encoding='utf-8') as file:
    auction_ended_template = file.read()


def send_user_won_auction_email(buyer: User, auction: Auction) -> None:
    email_data = {
        'user': {
            'address': {
                'street': buyer.billing_details.address,
                'city': buyer.billing_details.city,
                'state': buyer.billing_details.state,
                'postal_code': buyer.billing_details.postal_code,
                'country': buyer.billing_details.country
            },
            'username': buyer.username,
            'email': buyer.email,
            'current_balance': buyer.balance_total,
            'balance_reserved': buyer.balance_reserved,
        },
        'auction': {
            'title': auction.product.name,
            'current_price': auction.bid.current_bid_value,
            'end_date': auction.end_date,
        }
    }

    template = Template(auction_won_template)

    # Renderowanie szablonu z danymi
    rendered_html = template.render(email_data=email_data)

    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=buyer.email,
            subject=f"Charfair - You won an auction!",
            html_content=rendered_html
        )

        client = SendGridAPIClient(SENDGRID_API_KEY)
        response = client.send(message)

        if response.status_code != 202:
            logger.error(
                f"Failed to send user won auction, body {response.body} status code {response.status_code} headers {response.headers}")
        else:
            logger.trace(f"send_user_won_auction_email: email sent to {buyer.email}")
    except Exception as e:
        logger.error(f"Failed to send user won auction, error {str(e)}")


def send_seller_auction_completed_email(seller_email: str, buyer: User, auction: Auction) -> None:
    email_data = {
        'user': {
            'address': {
                'street': buyer.billing_details.address,
                'city': buyer.billing_details.city,
                'state': buyer.billing_details.state,
                'postal_code': buyer.billing_details.postal_code,
                'country': buyer.billing_details.country
            },
            'username': buyer.username,
            'email': buyer.email,
        },
        'auction': {
            'title': auction.product.name,
            'current_price': auction.bid.current_bid_value,
            'end_date': auction.end_date,
        }
    }

    template = Template(auction_ended_template)

    # Renderowanie szablonu z danymi
    rendered_html = template.render(email_data=email_data)

    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=seller_email,
            subject=f"Charfair - Your auction has ended!",
            html_content=rendered_html
        )

        client = SendGridAPIClient(SENDGRID_API_KEY)
        response = client.send(message)

        if response.status_code != 202:
            logger.error(
                f"Failed to send seller auction completed, body {response.body} status code {response.status_code} headers {response.headers}")
        else:
            logger.trace(f"send_seller_auction_completed_email: email sent to {seller_email}")

    except Exception as e:
        logger.error(f"Failed to send seller auction completed, error {str(e)}")
