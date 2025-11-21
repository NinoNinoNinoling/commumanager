"""REST API 라우트"""
from flask import Blueprint, request, jsonify, session
from admin_web.services.user_service import UserService
from admin_web.services.item_service import ItemService
from admin_web.models.item import Item

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def require_auth():
    """간단한 인증 체크"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return None


@api_bp.route('/users', methods=['GET'])
def get_users():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_service = UserService()
    users = user_service.get_all_users()
    return jsonify({'users': [u.to_dict() for u in users]})


@api_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_service = UserService()
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()})


@api_bp.route('/users/<user_id>/balance', methods=['POST'])
def adjust_balance(user_id):
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    amount = data.get('amount')
    description = data.get('description', '관리자 조정')
    
    user_service = UserService()
    try:
        result = user_service.adjust_balance(user_id, amount, 'adjustment', description, session.get('user_id'))
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/items', methods=['GET'])
def get_items():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    item_service = ItemService()
    items = item_service.get_active_items()
    return jsonify({'items': [i.to_dict() for i in items]})


@api_bp.route('/items', methods=['POST'])
def create_item():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    item = Item.from_dict(data)
    
    item_service = ItemService()
    try:
        result = item_service.create_item(item)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/dashboard/stats', methods=['GET'])
def get_stats():
    auth_error = require_auth()
    if auth_error:
        return auth_error
    
    user_service = UserService()
    item_service = ItemService()
    
    users = user_service.get_all_users()
    items = item_service.get_active_items()
    
    stats = {
        'total_users': len(users),
        'total_items': len(items),
        'total_balance': sum(u.balance for u in users),
    }
    return jsonify({'stats': stats})
