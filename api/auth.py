from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
import logging

user_blueprint = Blueprint('user_blueprint', __name__)

@user_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not auth or not data['email'] or not data['password']:
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401

    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Debugging: Log the pulled user data and the provided password
        logging.debug(f"Pulled user data from DB: {user}")
        logging.debug(f"Provided password: {data['password']}")

        # Check if the provided password matches the stored password hash
        if check_password_hash(user.password, data['password']):
            token = create_access_token(identity=user.id)
            return jsonify({'token': token}), 200
        else:
            logging.debug("Password verification failed.")  # Additional debug information
            return jsonify({'message': 'Wrong credentials'}), 403

    except Exception as e:
        logging.error(f"Login error: {e}")  # Use logging for errors
        return jsonify({'error': str(e)}), 500

@user_blueprint.route('/register', methods=['POST'])
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
        language = data['language']
        # Company Info
        com_street = data['com_street']
        com_city = data['com_city']
        com_country = data['com_country']
        com_name = data['com_name']
        com_vat = data['com_vat']
        com_phone = data['com_phone']
        com_postal = data['com_postal']
        com_website = data['com_website']

        # Create a new User instance
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password,
                        language=language, com_street=com_street, com_city=com_city, com_country=com_country,
                        com_name=com_name, com_vat=com_vat, com_phone=com_phone, com_postal= com_postal, com_website=com_website)
        
        # Attempt to register the user
        if new_user.register_user_if_not_exist():
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
