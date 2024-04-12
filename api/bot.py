from flask import Blueprint, request, jsonify
from models import Bot
import os



bot_blueprint = Blueprint('bot_blueprint', __name__)

@bot_blueprint.route('/create_bot', methods=['POST'])
def create_bot():
    try:
        dat = request.form
        name = data['name']
        avatar = request.files['avatar']
        color = data['color'] 
        active = data['active'] 
        start_time = data['start_time'] 
        end_time = data['end_time'] 
        knowledge_base = data['knowledge_base']
        
        if avatar:
            filename = secure_file(avatar.filename)
            avatar.save(os.path.join(app.config['UPLOAD_FOLDER']))
        new_bot = Bot(name=name, avatar=filename, color=color, active=active, start_time=start_time, end_time=end_time, knowledge_base=knowledge_base)
        new_bot.save()

        return jsonify({'message': 'Success'}), 201
    except:
        return jsonify({'error':'Server is busy!'}), 500

