from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import  create_access_token, create_refresh_token,  jwt_required, get_jwt_identity, set_access_cookies
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import cross_origin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from models import User, Bot
from flask_mail import Mail, Message
import logging
import hashlib
from api.mautic import get_access_token, create_mautic_user, update_mautic_user, login_mautic
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
        logging.debug(f"Pulled user data from DB: {user}")
        logging.debug(f"Provided password: {data['password']}")
        mautic_data = {}
        # Check if the provided password matches the stored password hash
        if check_password_hash(user.password, data['password']):
            total_bots = Bot.query.filter_by(user_id=user.id).count()
            active_bots = Bot.query.filter_by(user_id=user.id, active=1).count()
            mautic_data["language"] = user.language
            mautic_data["bots_active"] = active_bots
            mautic_data["bots_registered"] = total_bots
            if login_mautic(mautic_data, user.mauticId) == 'error':
                return jsonify({'error': 'Server is busy. Try again later!'}), 400
                
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify({'accessToken': access_token, 'refreshToken':refresh_token, 'userId':user.id}), 200
            # set_access_cookies(response, token)
        else:
            logging.debug("Password verification failed.")  # Additional debug information
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
            return jsonify({'error': 'User already exists'}), 409
        # Create a new User instance
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, mauticId=76, botsActive=0,
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

    msg = Message('Password Reset Link', sender='legendarystar2160187@gmail.com', recipients=[email])

    reset_url = f'http://localhost:3000/reset-password/{token}'

    emailContent = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Your Password</title>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 16px; color: #333; }}
            .container {{ width: 100%; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9; }}
            .button {{ display: block; width: 200px; height: 50px; margin: 20px auto; background-color: #4CAF50; color: white; border: none; border-radius: 5px; text-align: center; text-decoration: none; line-height: 50px; font-size: 16px; text-color:white; font-weight:bold }}
            .footer {{ font-size: 14px; text-align: center; color: #777; }}
        </style>
        </head>
        <body>
        <div class="container">
            <h2>Reset Your Password</h2>
            <p>Hello,</p>
            <p>You recently requested to reset your password for your account. Click the button below to reset it.</p>
            <a href="{reset_url}" class="button">Reset Your Password</a>
            <p>If you did not request a password reset, please ignore this email or contact support if you have questions.</p>
            <p>Thanks,<br>AIANA Team</p>
            <div class="footer">
                <p>If you’re having trouble clicking the "Reset Your Password" button, copy and paste the URL below into your web browser:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
            </div>
        </div>
        </body>
        </html>"""

    msg.html = emailContent
    mail = Mail(current_app)
    mail.send(msg)

    return jsonify({'message': 'Password reset link sent to email!'}), 200

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
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 201