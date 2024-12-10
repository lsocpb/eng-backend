import os

from jinja2 import Template
from sendgrid import Mail, SendGridAPIClient

from db_management.models import User, Auction
from utils.constants import fastapi_logger as logger

send_real_emails = True

with open("templates/auction_won.html", "r", encoding='utf-8') as file:
    auction_won_template = file.read()

with open("templates/auction_completed.html", "r", encoding='utf-8') as file:
    auction_ended_template = file.read()


def _send_email(to_email: str, subject: str, html_content: str) -> None:
    if not send_real_emails:
        logger.info(f"Email not sent to {to_email} because send_real_emails is set to False")
        return
    try:
        message = Mail(
            from_email=os.getenv("SENDGRID_FROM_EMAIL"),
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        client = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = client.send(message)

        if response.status_code != 202:
            logger.error(
                f"Failed to send email, body {response.body} status code {response.status_code} headers {response.headers}")
        else:
            logger.trace(f"Email sent to {to_email}")

    except Exception as e:
        logger.error(f"Failed to send email, error {str(e)}")


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

    _send_email(buyer.email, f"Charfair - You won an auction!", rendered_html)


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

    _send_email(seller_email, f"Charfair - Your auction has ended!", rendered_html)


def send_password_reset_email(email: str, reset_link: str) -> None:
    rendered_html = f"Click <a href='{reset_link}'>here</a> to reset your password<br>If your email client does not support " \
                    f"clicking the link, copy and paste the following URL into your browser: {reset_link} "

    _send_email(email, f"Charfair - Password reset", rendered_html)
