from flask import Blueprint, request, jsonify, current_app
from dotenv import load_dotenv
import os
import stripe
import json
from models import User, BillingPlan

load_dotenv()

payment_blueprint = Blueprint('payment_blueprint', __name__)

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "endpoint_secret":os.environ["STRIPE_ENDPINT_SECRET"]
}
domain_url = os.environ["FRONTEND_DOMAIN"]

stripe.api_key = stripe_keys["secret_key"]


print(stripe_keys["secret_key"])
print(stripe_keys["publishable_key"])
print(stripe_keys["endpoint_secret"])

# @payment_blueprint.route('/create-checkout-session', methods=['POST'])
# def create_checkout_session():
#     try:
#         # Create new checkout session for the order
#         data = request.get_json()
#         checkoutSession = stripe.checkout.Session.create (
#             payment_method_types=["card"],
#             mode="subscription",
#             line_items=[{"price":data["price_id"], "quantity":1}],
#             success_url=f"{domain_url}/success?session_id={CHECKOUT_SESSION_ID}",
#             cancel_url=f"{domain_url}/cancel",
#         )

#         return jsonify({"sessionId":checkoutSession.id})
    
#     except Exception as e:
#         return jsonify(error=str(e)), 403

def create_customer_id(email):
    customer = stripe.Customer.create(email=email)
    return customer.id

@payment_blueprint.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=False)
    sig_header = request.headers.get("Stripe-Signature")
    # print("payload--<", payload)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        print(str(e))
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(str(e))
        return "Invalid signature", 400
   
    # Handle the checkout.session.completed event
    if event["type"] == "customer.subscription.created":
        subscription = event['data']['object']
        prod_id = subscription['plan']['product']
        # print(prod_id)
        customer_id = subscription['customer']
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer['email']
        # print(customer_email)
        user = User.query.filter_by(email=customer_email).first()
        # print(user)
        if user:
            user.stripe_customer_id = customer_id
            plan = BillingPlan.query.filter_by(prod_id=prod_id).first()
            print(plan.code)
            user.billing_plan = plan.code
            user.status = 'active'
            user.save()
        print("Subscription created")

    if event["type"] == "checkout.session.completed":
        print("Payment was successful.")
        # print(event['data']['object'])
        subscription = event['data']['object']
        # customer_email = subscription.customer_email
        prod_id = subscription['plan']['product']
        print(prod_id)
        customer_id = subscription['customer']
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer['email']
        # print(customer_email)
        user = User.query.filter_by(email=customer_email).first()
        # print(user)
        if user:
            user.stripe_customer_id = customer_id
            plan = BillingPlan.query.filter_by(prod_id=prod_id).first()
            print(plan.code)
            user.billing_plan = plan.code
            user.save()
        # product_id = subscription['price']['product']
        # print("Customer --->  ", customer_email)
        # print("Product --->  ", product_id)
        # TODO: run some custom code here
    
    if event["type"] == "customer.subscription.updated":
        # print(event['data']['object'])
        subscription = event['data']['object']
        prod_id = subscription['plan']['product']
        print(prod_id)
        customer_id = subscription['customer']
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer['email']
        # print(customer_email)
        user = User.query.filter_by(email=customer_email).first()
        # print(user)
        if user:
            user.stripe_customer_id = customer_id
            plan = BillingPlan.query.filter_by(prod_id=prod_id).first()
            print(plan.code)
            user.billing_plan = plan.code
            user.save()

        # plan_id = subscription['items']['data'][0]['price']['product']
        print("Updated")
    
    if event["type"] == "customer.subscription.paused":
        print("Paused")

    if event["type"] == "subscription_schedule.canceled":
        print("Plan canceled!")
    
    if event["type"] == "invoice.payment_succeeded":
        print("Invoice paid")
    
    if event["type"] == "invoice.payment_failed":
        subscription = event['data']['object']
        prod_id = subscription['plan']['product']
        # print(prod_id)
        customer_id = subscription['customer']
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer['email']
        # print(customer_email)
        user = User.query.filter_by(email=customer_email).first()
        # print(user)
        if user:
            user.stripe_customer_id = customer_id
            user.billing_plan = "aiana_try"
            user.save()

        print("Update user profile")
    # Subscription deleted
    if event["type"] == "customer.subscription.deleted":
        subscription = event['data']['object']
        prod_id = subscription['plan']['product']
        # print(prod_id)
        customer_id = subscription['customer']
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer['email']
        # print(customer_email)
        user = User.query.filter_by(email=customer_email).first()
        # print(user)
        if user:
            user.stripe_customer_id = customer_id
            
            user.billing_plan = "aiana_try"
            user.status = 'cancel'
            user.save()
        print("Update user profile")
    return "Success", 200