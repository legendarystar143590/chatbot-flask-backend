from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import  create_access_token, create_refresh_token,  jwt_required, get_jwt_identity, set_access_cookies
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import cross_origin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from models import User, Bot
import logging
import hashlib
import datetime
from api.mautic import get_access_token, create_mautic_user, update_mautic_user, login_mautic, mautic_reset_password
from utils.common import get_language_code


user_blueprint = Blueprint('user_blueprint', __name__)

@user_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data['email'] or not data['password']:
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401

    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'error': 'User not found.'}), 403

        # Debugging: Log the pulled user data and the provided password
        print(f"Pulled user data from DB: {user}")
        print(f"Provided password: {data['password']}")
        mautic_data = {}
        # Check if the provided password matches the stored password hash
        if check_password_hash(user.password, data['password']):
            total_bots = Bot.query.filter_by(user_id=user.id).count()
            active_bots = Bot.query.filter_by(user_id=user.id, active=1).count()
            mautic_data["language"] = user.language
            mautic_data["bots_active"] = active_bots
            mautic_data["bots_registered"] = total_bots
            # if login_mautic(mautic_data, user.mauticId) == 'error':
            #     return jsonify({'error': 'Server is busy. Try again later!'}), 400
                
            access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=1))
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify({'accessToken': access_token, 'refreshToken':refresh_token, 'userId':user.id}), 200
            # set_access_cookies(response, token)
        else:
            print("Password verification failed.")  # Additional debug information
            return jsonify({'error': 'Wrong credentials'}), 403

    except Exception as e:
        logging.error(f"Login error: {e}")  # Use logging for errors
        return jsonify({'error': str(e)}), 500

@user_blueprint.route('/register', methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        # User Info
        first_name = data['first_name']
        last_name = data['last_name']
        email = data['email']
        password = generate_password_hash(data['password'])
        language = get_language_code(data['language'])
    
        # Company Info
        com_street = data['com_street']
        com_city = data['com_city']
        com_country = data['com_country']
        com_name = data['com_name']
        com_vat = data['com_vat']
        com_street_number = data['com_street_number']
        com_postal = data['com_postal']
        com_website = data['com_website']
        data['language'] = language
        mauticId = create_mautic_user(data)
        if mauticId == 'error':
            return jsonify({'error': 'Invalid email!'}), 400
        # Create a new User instance
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, mauticId=mauticId, botsActive=0,
                        language=language, com_street=com_street, com_city=com_city, com_country=com_country,
                        com_name=com_name, com_vat=com_vat, com_street_number=com_street_number, com_postal= com_postal, com_website=com_website)
        
        # Attempt to register the user
        if new_user.register_user_if_not_exist():
            print("Starting...")
            return jsonify({'message': 'User registered successfully'}), 201
        else:
            return jsonify({'error': 'User already exists'}), 409

    except KeyError as e:
        # If any key is missing in the data
        return jsonify({'error': f'Missing key in data: {e}'}), 400
    except Exception as e:
        # For any other errors
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

@user_blueprint.route('get_user', methods=['POST'])
@cross_origin()
@jwt_required()
def get_user():
    data = request.get_json()
    userID = data['userID']
    user = User.get_by_userID(userID)
    if user:
        return user.json(), 200
    else:
        return jsonify({'error': 'Not found user!'}), 400

@user_blueprint.route('update_user', methods=['POST'])
@cross_origin()
@jwt_required()
def update_user():
    data = request.get_json()
    user = User.get_by_userID(data['userID'])
    if user:
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.language = get_language_code(data['language'])
        user.password = generate_password_hash(data['password'])
        user.com_name = data['com_name']
        user.com_vat = data['com_vat']
        user.com_street = data['com_street']
        user.com_city = data['com_city']
        user.com_country = data['com_country']
        user.com_street_number = data['com_street_number']
        user.com_website = data['com_website']
        user.com_postal = data['com_postal']
        data["botsActive"] = user.botsActive
        if update_mautic_user(data, user.mauticId) == 'error':
            return jsonify({'error': 'Not found user!'}), 400
        user.save()
        return jsonify({'message': 'success'}), 201
    else:
        return jsonify({'error': 'Not found user!'}), 400

@user_blueprint.route('/forgot_password', methods=['POST'])
@cross_origin()
def forgot_password():
    data = request.get_json()
    email = data['email']
    user = User.get_by_email(email)

    if not user:
        return 'User not found', 404
    
    # Generate a token
    serializer = URLSafeTimedSerializer(current_app.config['JWT_SECRET_KEY'])
    token = serializer.dumps(email, salt='email-confirm')

    url = request.host_url + 'reset/l'
    user = User.query.filter_by(email=email).first()

    reset_url = f'http://localhost:3000/reset-password/{token}'
    data['password_reset_link'] = reset_url
    if mautic_reset_password(data, user.mauticId) == 1:
        return jsonify({'message': 'Password reset link sent to email!'}), 200
    else:
        return jsonify({'message': 'Error sending email!'}), 500

@user_blueprint.route('/reset_with_token', methods = ['GET', 'POST'])
@jwt_required()
def reset_with_token():
    data = request.get_json()
    print(data)
    password = data['password']
    token = data['token']
    print(current_app.config['JWT_SECRET_KEY'])
    serializer = URLSafeTimedSerializer(current_app.config['JWT_SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        print(email)
        user = User.get_by_email(email)
        user.password = generate_password_hash(password)
        user.save()

        return jsonify({'message': 'success'}), 201
        
    except SignatureExpired:
        return jsonify({'message': 'The password reset link is expired'}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'message':'Server Error'}), 500

@user_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user, expires_delta=datetime.timedelta(hours=1))
    return jsonify(access_token=new_access_token), 201