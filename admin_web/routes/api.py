"""REST API 라우트"""
from functools import wraps
from flask import Blueprint, request, jsonify, session

# Models
from admin_web.models.item import Item

# Dependencies (DI)
from admin_web.dependencies import (
    get_user_service,
    get_dashboard_service,
    get_warning_service,
    get_item_service,
    get_settings_service
)

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def require_auth(f):
    """
    인증을 요구하는 라우트를 위한 데코레이터
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/users', methods=['GET'])
@require_auth
def get_users():
    user_service = get_user_service()
    users = user_service.get_all_users()
    return jsonify({'users': [u.to_dict() for u in users]})


@api_bp.route('/users/risk', methods=['GET'])
@require_auth
def get_risk_users():
    user_service = get_user_service()
    risk_users = user_service.get_risk_users() 
    return jsonify({'users': risk_users})


@api_bp.route('/users/<user_id>', methods=['GET'])
@require_auth
def get_user_api(user_id):
    user_service = get_user_service()
    user = user_service.get_user(user_id)
    
    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({'error': 'User not found'}), 404


@api_bp.route('/users/<user_id>/role', methods=['PATCH'])
@require_auth
def patch_user_role(user_id):
    data = request.get_json()
    new_role = data.get('role')
    
    if not new_role:
        return jsonify({'error': 'Role is required'}), 400

    user_service = get_user_service()
    try:
        updated_user = user_service.update_user_role(user_id, new_role)
        return jsonify(updated_user.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/users/<user_id>/balance', methods=['POST'])
@require_auth
def adjust_balance(user_id):
    data = request.get_json()
    amount = data.get('amount')
    description = data.get('description', '관리자 조정')
    admin_id = session.get('user_id')

    user_service = get_user_service()
    try:
        result = user_service.adjust_balance(user_id, amount, 'adjustment', description, admin_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/items', methods=['GET'])
@require_auth
def get_items():
    item_service = get_item_service()
    items = item_service.get_active_items()
    return jsonify({'items': [i.to_dict() for i in items]})


@api_bp.route('/items', methods=['POST'])
@require_auth
def create_item():
    data = request.get_json()
    try:
        item = Item.from_dict(data)
        item_service = get_item_service()
        result = item_service.create_item(item)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/dashboard/stats', methods=['GET'])
@require_auth
def get_stats():
    dashboard_service = get_dashboard_service()
    stats = dashboard_service.get_dashboard_stats()
    return jsonify({'stats': stats})


@api_bp.route('/settings', methods=['POST'])
@require_auth
def update_settings():
    data = request.get_json()
    settings_list = data.get('settings')
    if not settings_list:
        return jsonify({'error': 'No settings provided'}), 400

    admin_user = session.get('user_id', 'unknown')
    
    settings_service = get_settings_service()
    result = settings_service.update_settings(settings_list, admin_user)

    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code


@api_bp.route('/warnings', methods=['POST', 'GET'])
@require_auth
def handle_warnings():
    warning_service = get_warning_service()
    
    if request.method == 'GET':
        warnings = warning_service.get_all_warnings()
        return jsonify({'warnings': warnings})
        
    elif request.method == 'POST':
        data = request.get_json()
        try:
            result = warning_service.create_warning(data)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400


@api_bp.route('/users/<user_id>/warnings', methods=['GET'])
@require_auth
def get_warnings_for_user(user_id):
    warning_service = get_warning_service()
    warnings = warning_service.get_user_warnings(user_id)
    return jsonify({'warnings': warnings})
