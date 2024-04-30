from flask import Blueprint, request, jsonify



chat_blueprint = Blueprint('chat_blueprint', __name__)

@chat_blueprint.route('query', methods=['POST'])
def query():
    data = request.get_json()
    user_id = data['userId']
    bot_id = data['botId']
    query = data['query']
    