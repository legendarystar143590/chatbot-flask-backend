from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import Bot
import os



bot_blueprint = Blueprint('bot_blueprint', __name__)

@bot_blueprint.route('/create_bot', methods=['POST'])
def create_bot():
    try:
        data = request.form
        # print(data)
        name = data['name']
        print(name)
        avatar = request.files.get('avatar')
        color = data['color'] 
        active = data.get('active') == 'true'
        start_time = data['start_time'] 
        end_time = data['end_time'] 
        knowledge_base = data['knowledge_base']
        filename = None
        if avatar:
            # Generate a unique file name using uuid4 and preserve the file extension
            extension = os.path.splitext(secure_filename(avatar.filename))[1]
            unique_filename = str(uuid.uuid4()) + extension
            
            # Save the file using the new unique filename within the configured upload folder
            avatar.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
            filename = unique_filename
        else:
            filename = None
        new_bot = Bot(name=name, avatar=filename, color=color, active=active, start_time=start_time, end_time=end_time, knowledge_base=knowledge_base)
        new_bot.save()

        return jsonify({'message': 'Success'}), 201
    except Exception as e:
        print(e)
        return jsonify({'error':'Server is busy!'}), 500

