"""REST API 라우트"""
from functools import wraps
from flask import Blueprint, request, jsonify, session

# Services
from admin_web.services.user_service import UserService
from admin_web.services.item_service import ItemService
from admin_web.services.settings_service import SettingsService
from admin_web.services.dashboard_service import DashboardService
from admin_web.services.warning_service import WarningService

# Models
from admin_web.models.item import Item

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
    """
    user_service = UserService()
    risk_users = user_service.get_risk_users() 
    return jsonify({'users': risk_users})


@api_bp.route('/users/<user_id>', methods=['GET'])
@require_auth
def get_user_api(user_id):
    """유저 상세 정보 조회"""
    user_service = UserService()
    user = user_service.get_user(user_id)
    
    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({'error': 'User not found'}), 404


@api_bp.route('/users/<user_id>/role', methods=['PATCH'])
@require_auth
def patch_user_role(user_id):
    """유저 역할 변경"""
    data = request.get_json()
    new_role = data.get('role')
    
    if not new_role:
        return jsonify({'error': 'Role is required'}), 400

    user_service = UserService()
    try:
        updated_user = user_service.update_user_role(user_id, new_role)
        return jsonify(updated_user.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/users/<user_id>/balance', methods=['POST'])
@require_auth
def adjust_balance(user_id):
    """유저 잔액 조정"""
    data = request.get_json()
    amount = data.get('amount')
    description = data.get('description', '관리자 조정')
    
    # 관리자 정보 (세션에서 가져옴)
    admin_id = session.get('user_id')

    user_service = UserService()
    try:
        result = user_service.adjust_balance(user_id, amount, 'adjustment', description, admin_id)
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
    try:
        item = Item.from_dict(data)
        item_service = ItemService()
        result = item_service.create_item(item)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/dashboard/stats', methods=['GET'])
@require_auth
def get_stats():
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

    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code


@api_bp.route('/warnings', methods=['POST', 'GET'])
@require_auth
def handle_warnings():
    warning_service = WarningService()
    
    if request.method == 'GET':
        warnings = warning_service.get_all_warnings()
        return jsonify({'warnings': warnings})
        
    elif request.method == 'POST':
        data = request.get_json()
        try:
            # create_warning의 시그니처에 맞춰 데이터 전달
            result = warning_service.create_warning(data)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400


@api_bp.route('/users/<user_id>/warnings', methods=['GET'])
@require_auth
def get_warnings_for_user(user_id):
    warning_service = WarningService()
    warnings = warning_service.get_user_warnings(user_id)
    return jsonify({'warnings': warnings})
