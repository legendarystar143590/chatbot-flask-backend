# from flask import Blueprint, Flask, request, jsonify, redirect, url_for, current_app
# from flask_jwt_extended import jwt_required
# from dotenv import load_dotenv
# import hmac
# import hashlib
# import base64
# import os
# from models import ShopInfo

# load_dotenv()

# SECRET_KEY = os.getenv("SHOPIFY_SECRET_KEY")
# SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
# REDIRECT_URI = os.getenv("REDIRECT_URL")

# shopify_blueprint = Blueprint('shopify_blueprint', __name__)

# def verify_webhook(data: bytes, hmac_header: str) -> bool:
#     """
#     Verifies the HMAC of incoming webhook data against a provided HMAC header.
#     """
#     digest = hmac.new(SECRET_KEY.encode('utf-8'), data, hashlib.sha256).digest()
#     computed_hmac = base64.b64encode(digest).decode('utf-8')
#     return hmac.compare_digest(computed_hmac, hmac_header)

# @shopify_blueprint.route('/shopifyauth/install', methods=['GET'])
# def install():
#     shop = request.args.get('shop')
#     timestamp = request.args.get('timestamp')
#     hmac_header = request.args.get('hmac')
#     state = request.args.get('state')
#     # Verify the webhook using the provided parameters
#     data = f'shop={shop}&timestamp={timestamp}&state={state}'.encode('utf-8')
#     if verify_webhook(data, hmac_header):
#         # Store the shop code and state securely (implement your own storage logic)
#         store_shop_data(shop, state)

#         # Redirect to Shopify authorization URL
#         return redirect(f'https://{shop}.myshopify.com/admin/oauth/authorize?client_id={SHOPIFY_API_KEY}&scope=read_products&redirect_uri={REDIRECT_URI}&state={state}')
    
#     return "Verification failed", 403

# @shopify_blueprint.route('/shopifyauth', methods=['GET'])
# def auth_callback():
#     code = request.args.get('code')
#     shop = request.args.get('shop')
#     state = request.args.get('state')
#     timestamp = request.args.get('timestamp')
#     hmac_header = request.args.get('hmac')

#     data = f'shop={shop}&code={code}&state={state}&timestamp={timestamp}'.encode('utf-8')
#     # Verify that state matches what was stored during installation
#     if verify_webhook(data, hmac_header):
#         if verify_state(shop, state):
#             # Store the hashed code with the shop code securely (implement your own storage logic)
#             store_hashed_code(shop, code)
#             return {'status':"success",'message':f'Authorization successful'}, 200
    
#     return "State verification failed", 403

# def store_shop_data(shop: str, state: str):
#     """
#     Store shop data securely (implement your own storage logic).
#     """
#     print(f"Storing shop: {shop}, state: {state}")

#     if ShopInfo.check_shop_exist(shop):
#         return jsonify({'error': 'Shop already exists'}), 409
    
#     new_shop = ShopInfo(shop=shop, state=state)


# def store_hashed_code(shop: str, code: str):
#     """
#     Store hashed authorization code securely (implement your own storage logic).
#     """
#     hashed_code = hash_code(code)  # Implement your hashing logic here
#     print(f"Storing hashed code for shop {shop}: {hashed_code}")

#     if ShopInfo.check_shop_exist(shop) == False:
#         return jsonify({'error':'Shop is not exist'}), 409
    
#     ShopInfo.update_shop_info(shop, code)

# def verify_state(shop: str, state: str) -> bool:
#     """
#     Verify that the state matches what was stored during installation.
#     """
#     # Implement your logic to retrieve and compare stored state
#     db_shop = ShopInfo.query.filter_by(shop=shop).first()
#     if db_shop.state == state:
#         return True  # Replace with actual comparison logic
#     return False

# def hash_code(code: str) -> str:
#     """
#     Hash the authorization code for secure storage.
#     """
#     return hashlib.sha256(code.encode()).hexdigest()