from flask import Blueprint, request, jsonify, current_app
from dotenv import load_dotenv
import os
import stripe

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
    
@payment_blueprint.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")
    # print("payload--<", payload)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload\
        print(str(e))
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(str(e))
        return "Invalid signature", 400
    print(event['type'])
    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        print("Payment was successful.")

        # TODO: run some custom code here
    
    if event["type"] == "customer.subscription.updated":
        print(event['data']['object'])
        subscription = event['data']['object']
        plan_id = subscription['items']['data'][0]['price']['product']
        print(plan_id)

    return "Success", 200