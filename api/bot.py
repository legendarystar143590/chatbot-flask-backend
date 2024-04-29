from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import Bot
from sqlalchemy.exc import IntegrityError
import uuid
from io import BytesIO
import os
import base64



bot_blueprint = Blueprint('bot_blueprint', __name__)

@bot_blueprint.route('/create_bot', methods=['POST'])
def create_bot():
    try:
        data = request.form
        # print(data)
        name = data['name']
        user_id = data['user_id']
        avatar = request.files.get('avatar')
        color = data['color'] 
        active = data.get('active') == 'true'
        start_time = data['start_time'] 
        end_time = data['end_time'] 
        knowledge_base = data['knowledge_base']
        print("Avatar >>>",avatar)
        if avatar:
            img_bytes = BytesIO()
            avatar.save(img_bytes)
            img_bytes.seek(0)
            bin_image = img_bytes.read()
        else:
            bin_image = None
        new_bot = Bot(user_id = user_id, name=name, avatar=bin_image, color=color, active=active, start_time=start_time, end_time=end_time, knowledge_base=knowledge_base)
        new_bot.save()

        return jsonify({'message': 'Success'}), 201

    except IntegrityError as e:  # Catch integrity errors specifically
        db.session.rollback()  # Rollback the session to a clean state
        print(e)
        return jsonify({'error':'A bot with this name already exists!'}), 409  # Return a conflict HTTP status code

    except Exception as e:
        print(e)
        return jsonify({'error':'Server is busy!'}), 500

@bot_blueprint.route('/get_chatbots', methods=['GET'])
def get_chatbots():
    try:
        user_id = request.args.get('userId')
        print(user_id)
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        bots = Bot.query.filter_by(user_id=user_id).all()
        bot_list = []
        for bot in bots:
            bot_data = bot.json()  # Assuming that this method converts the bot instance to a dict
            if bot.avatar:  # Check if the bot has an avatar
                avatar_encoded = base64.b64encode(bot.avatar).decode('utf-8')  # Encode the binary data to base64
                bot_data['avatar'] = f"data:image/png;base64,{avatar_encoded}"  # Prepend the necessary prefix
            else:
                bot_data['avatar'] = None  # No avatar case
            bot_list.append(bot_data)

        return jsonify(bot_list), 200
    except ValueError:
        # If the provided user_id cannot be converted to an integer, return an error
        return jsonify({'error': 'Invalid user_id format. It should be an integer.'}), 400