from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import Bot, KnowledgeBase, Conversation
from sqlalchemy.exc import IntegrityError
from utils.provider import generate
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

    except Exception as e:
        print(e)
        return jsonify({'error':'Server is busy!'}), 500

@bot_blueprint.route('/get_chatbots', methods=['GET'])
def get_chatbots():
    try:
        user_id = request.args.get('userId')
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

@bot_blueprint.route('/get_chatbot', methods=['GET'])
def get_chatbot():
    try:
        bot_id = request.args.get('botId')
        if not bot_id:
            return jsonify({'error': 'bot_id is required'}), 400

        bot = Bot.query.filter_by(id=bot_id).first()
        
        bot_data = bot.json()
        # print(bot_data)
        if bot.avatar:  # Check if the bot has an avatar
            avatar_encoded = base64.b64encode(bot.avatar).decode('utf-8')  # Encode the binary data to base64
            bot_data['avatar'] = f"data:image/png;base64,{avatar_encoded}"  # Prepend the necessary prefix
        else:
            bot_data['avatar'] = None  # No avatar case
        knowledge_base = KnowledgeBase.query.filter_by(unique_id=bot_data['knowledge_base']).first()
        bot_data['knowledge_base'] = knowledge_base.name
        return jsonify(bot_data), 200

    except ValueError:
        # If the provided user_id cannot be converted to an integer, return an error
        return jsonify({'error': 'Invalid bot_id format. It should be an integer.'}), 400

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Server error.'}), 400

@bot_blueprint.route('/update_chatbot', methods=['POST'])
def update_chatbot():
    try:
        botId = request.args.get('botId')
        data = request.form
        # Retrieve the existing knowledge base entry using the provided botId
        bot = Bot.query.filter_by(id=botId).first()
        if not bot:
            return jsonify({"error": "Knowledge base entry not found."}), 404
       
        # Extract the relevant information from the form
        name = data['name']
        user_id = data['user_id']
        avatar = request.files.get('avatar')
        color = data['color'] 
        active = data.get('active') == 'true'
        start_time = data['start_time'] 
        end_time = data['end_time'] 
        knowledge_base = data['knowledge_base']
        if avatar:
            img_bytes = BytesIO()
            avatar.save(img_bytes)
            img_bytes.seek(0)
            bin_image = img_bytes.read()
        else:
            bin_image = None
        bot.name = name
        bot.avatar = bin_image
        bot.color = color
        bot.active = active
        bot.start_time = start_time
        bot.end_time = end_time
        bot.knowledge_base = knowledge_base
        bot.save()

        return jsonify({'message': 'Success'}), 201
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Server error"}), 500
        
@bot_blueprint.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        query = data['query']
        bot_id = data['bot_id']
        user_id = data['user_id']
        session_id = data['session_id']
        if bot_id:
            bot = Bot.query.filter_by(id=bot_id).first()
        knowledge_base = bot.knowledge_base
        result = generate(bot_id, session_id, query, knowledge_base)

        return jsonify({'message': result}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Server Error'}), 500

@bot_blueprint.route('/del_messages', methods=['POST'])
def del_messages():
    try:
        data = request.get_json()
        bot_id = data['bot_id']
        Conversation.del_by_bot_id(bot_id)
        return jsonify({'status': 'success'}), 201
        
    except Exception as e:
        print(str(e))
        return jsonify({'status':'error'}), 500
    
