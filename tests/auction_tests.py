import os

from jinja2 import Template
from sendgrid import Mail, SendGridAPIClient

# change the path to the root of the project
os.chdir("..")

import repos.auction_repo
import repos.user_repo
# from controllers.user_controller import SENDGRID_FROM_EMAIL, SENDGRID_API_KEY
from db_management.dto import CreateAuction, CreateAuctionProduct
from db_management.models import *
from repos.stats_repo import *
from response_models.user_responses import EmailSchema
from utils.constants import AuctionType


def create_sample_auction() -> CreateAuction:
    image = ["http://res.cloudinary.com/dsfdvlauw/image/upload/v1729090419/kjqwpkyxr4gfrmvtyhvu.jpg"]
    product = CreateAuctionProduct(name="Drzewo mądrości", description="Drzewo mądrości", category_id=1, images=image)

    custom_date = datetime(2024, 10, 20, 12, 30, 0)  # Custom date and time
    auction = CreateAuction(auction_type=AuctionType.BID, end_date=custom_date, price=1.0,
                            product=product)
    print(auction.dict())

    return auction


def stats_test(session: Session):
    user = repos.user_repo.get_by_id(session, 3)
    if user is None:
        raise ValueError("User not found")

    auction = repos.auction_repo.get_auction_by_id(session, 4)
    if auction is None:
        raise ValueError("Auction already exists")

    print(f"Auction: {auction.product.name} User: {user.username} User selling: {user.products_sold}")

    print(f"Registered users: {get_registered_useres_count(session)}")
    print(f"Auction count: {get_auction_count(session)}")
    print(f"Total bids: {get_total_bids_count(session)}")
    print(f"Total value of ended auctions: {get_total_value_of_ended_auctions(session)}")


def clear_all_auctions(session: Session):
    auctions = session.query(Auction).all()
    for auction in auctions:
        session.delete(auction)
    session.commit()


def template_email():
    #                 <p><strong>Street:</strong> {{ email_data.buyer.address.street }}</p>
    #                 <p><strong>City:</strong> {{ email_data.buyer.address.city }}</p>
    #                 <p><strong>State:</strong> {{ email_data.buyer.address.state }}</p>
    #                 <p><strong>Postal Code:</strong> {{ email_data.buyer.address.postal_code }}</p>
    #                 <p><strong>Country:</strong> {{ email_data.buyer.address.country }}</p>

    # <p>Dear {{ email_data.buyer.username }},</p>
    # <p><strong>Item Name:</strong> {{ email_data.auction.title }}</p>
    # <p><strong>Final Price:</strong> {{ email_data.auction.current_price }}</p>
    # <p><strong>End Date:</strong> {{ email_data.auction.end_date }}</p>
    # <p><strong>Name:</strong> {{ email_data.buyer.username }}</p>
    # <p><strong>Email:</strong> {{ email_data.buyer.email }}</p>
    email_data = {
        'buyer': {
            'address': {
                'street': '123 Main',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'country': 'USA'
            },
            'username': 'John Doe',
            'email': 'a@gmail.com',
        },
        'auction': {
            'title': 'Luxury Watch',
            'current_price': 1500.50,
            'end_date': '2024-10-30'
        }
    }

    f = open("../templates/auction_won.html", "r")
    template = Template(f.read())

    # Renderowanie szablonu z danymi
    rendered_html = template.render(email_data=email_data)

    print(rendered_html)
    with open("auction_won_rendered.html", "w") as file:
        file.write(rendered_html)


def email_test():
    email_data = EmailSchema(name="John Doe", email="test@gmail.com", message="Hello, this is a test message",
                             to="kacper.gc.15@gmail.com")
    try:
        message = Mail(
            from_email=os.getenv("SENDGRID_FROM_EMAIL"),
            to_emails="kacper.gc.15@gmail.com",
            subject=f"New message from {email_data.name}",
            html_content=f"""
                    <strong>Name:</strong> {email_data.name}<br>
                    <strong>Email:</strong> {email_data.email}<br>
                    <br>
                    <strong>Message:</strong><br>
                    {email_data.message}
                    """
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(response)
        print(response.status_code)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise ValueError(str(e))


def email_test2():
    user = repos.user_repo.get_by_id(session, 16)
    if user is None:
        raise ValueError("User not found")

    auction = repos.auction_repo.get_full_auction_by_id(session, 15)
    if auction is None:
        raise ValueError("Auction already exists")

    print(auction.to_public())
    # services.email_service.send_seller_auction_completed_email(user, auction)


if __name__ == '__main__':

    from db_management.database import create_db, session_maker

    create_db()
    # get session
    with session_maker() as session:
        email_test2()
        # template_email()
# create_sample_auction()
# stats_test(session)
# Tworzenie obiektu szablonu

#
# companyBilling1 = CompanyBilling(company_details="company_details1")
# companyBilling2 = CompanyBilling(company_details="company_details2")
# userBilling1 = UserBilling(details="user_details1")
# userBilling2 = UserBilling(details="user_details2")
#
# u1 = repos.user_repo.get_by_id(session, 3)
# u2 = repos.user_repo.get_by_id(session, 4)
# u3 = repos.user_repo.get_by_id(session, 5)
# u4 = repos.user_repo.get_by_id(session, 6)
#
# print(u1.billing_details)
# print(u2.billing_details)
# print(u3.billing_details)
# print(u4.billing_details)

# session.commit()

# services.auction_service.place_bid(auction.id, buyer.id, 5.12345678)
