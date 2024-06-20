from flask import Blueprint, request, jsonify, current_app
from models import Bot, Order, ChatLog, User
from utils.provider import generate
from flask_jwt_extended import jwt_required
from datetime import datetime
from api.mautic import book_ticket

ticket_blueprint = Blueprint('ticket_blueprint', __name__)


@ticket_blueprint.route('/book', methods=['POST'])
def book():
    try:
        
        data = request.get_json()
        bot_id = data['botId']
        userIndex = data['userIndex']
        session_id = data['sessionId']
        email = data['email']
        content = data['content']
        user = User.get_by_index(userIndex)
        order = Order(session_id, user.id, userIndex, bot_id, email, "open", content)
        order.save()
        chat_log = ChatLog.get_by_session(session_id)
        chat_log.result = 'Email-Sent'
        chat_log.save()
        
        data['id'] = order.id
        data['link'] = 'https://login.aiana.io/tickets'
        data['created'] = order.created_at
        
        if book_ticket(data, user.mauticId) != 'error':
            return jsonify({'message': 'success'}), 201
        else:
            return jsonify({'message': 'error'}), 500

        
    except Exception as e:
        print(str(e))
        return jsonify({'message': 'error'}), 500
        
@ticket_blueprint.route('/get_tickets', methods=['POST'])
@jwt_required()
def get_tickets():
    try:
        data = request.get_json()
        user_id = data['userId']
        orders = Order.get_by_user(user_id)
        orders_list = []
        for order in orders:
            order_json = order.json()
            orders_list.append(order_json)

        return jsonify(orders_list), 200

    except Exception as e:
        print(str(e))
        return jsonify({'error':'Server Error'}), 500

@ticket_blueprint.route('/del_ticket', methods=['POST'])
@jwt_required()
def del_ticket():
    try:
        data = request.get_json()
        ticketId = data['currentItem']
        orders = Order.del_by_id(ticketId)
        return jsonify({'status':'success'}), 201

    except Exception as e:
        print(str(e))
        return jsonify({'status':'error'}), 500
