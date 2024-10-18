from stripe import StripeClient

client = StripeClient("sk_test_...")

client.payment_links.create()

# list customers
customers = client.customers.list()

# print the first customer's email
print(customers.data[0].email)

# retrieve specific Customer
customer = client.customers.retrieve("cus_123456789")

# print that customer's email
print(customer.email)