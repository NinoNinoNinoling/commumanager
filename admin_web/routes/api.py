"""REST API 라우트"""
from functools import wraps
from flask import Blueprint, request, jsonify, session
from admin_web.services.user_service import UserService
from admin_web.services.item_service import ItemService
from admin_web.services.settings_service import SettingsService
from admin_web.models.item import Item
from admin_web.controllers.warning_controller import create_warning


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
    user_service = UserService()
    users = user_service.get_all_users()
    return jsonify({'users': [u.to_dict() for u in users]})


@api_bp.route('/users/risk', methods=['GET'])
@require_auth
def get_risk_users():
    """
    위험 감지 유저 목록 조회 API
    HTML(AJAX)에서 호출하는 엔드포인트입니다.
    """
    user_service = UserService()
    # 시스템 계정이 필터링된 리스트를 가져옵니다.
    risk_users = user_service.get_risk_users() 
    return jsonify({'users': risk_users})


@api_bp.route('/users/<user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    user_service = UserService()
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()})


@api_bp.route('/users/<user_id>/balance', methods=['POST'])
@require_auth
def adjust_balance(user_id):
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
@require_auth
def get_items():
    item_service = ItemService()
    items = item_service.get_active_items()
    return jsonify({'items': [i.to_dict() for i in items]})


@api_bp.route('/items', methods=['POST'])
@require_auth
def create_item():
    data = request.get_json()
    item = Item.from_dict(data)

    item_service = ItemService()
    try:
        result = item_service.create_item(item)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/dashboard/stats', methods=['GET'])
@require_auth
def get_stats():
    from admin_web.services.dashboard_service import DashboardService

    dashboard_service = DashboardService()
    stats = dashboard_service.get_dashboard_stats()

    return jsonify({'stats': stats})


@api_bp.route('/settings', methods=['POST'])
@require_auth
def update_settings():
    """
    시스템 설정을 업데이트합니다.
    """
    data = request.get_json()
    settings_list = data.get('settings')
    if not settings_list:
        return jsonify({'error': 'No settings provided'}), 400

    admin_user = session.get('user_id', 'unknown')
    
    settings_service = SettingsService()
    result = settings_service.update_settings(settings_list, admin_user)

    if result.get('success'):
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@api_bp.route('/warnings', methods=['POST'])
@require_auth
def post_warning():
    return create_warning()
