"""
User Controller
유저 관련 HTTP 요청/응답을 처리
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from admin_web.services.user_service import UserService
from admin_web.config import Config

# Blueprint 생성
user_bp = Blueprint('user', __name__, url_prefix='/users')

# Service 인스턴스 (app context에서 초기화 필요)
user_service = None


def init_user_controller(app):
    """
    컨트롤러 초기화 (app factory에서 호출)

    Args:
        app: Flask app 인스턴스
    """
    global user_service
    db_path = app.config.get('DATABASE_PATH', 'economy.db')
    user_service = UserService(db_path)


def login_required(f):
    """로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """관리자 권한 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        user_id = session['user_id']
        if not user_service.is_admin(user_id):
            return jsonify({'error': '관리자 권한이 필요합니다'}), 403

        return f(*args, **kwargs)
    return decorated_function


@user_bp.route('/', methods=['GET'])
@admin_required
def list_users():
    """
    유저 목록 조회 (페이지네이션)
    GET /users?page=1&per_page=20
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 페이지 번호 유효성 검사
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # 서비스 호출
        result = user_service.get_users_paginated(page=page, per_page=per_page)

        # HTML 렌더링 또는 JSON 반환
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(result)

        return render_template('users/list.html', **result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id: int):
    """
    특정 유저 정보 조회
    GET /users/<user_id>
    """
    try:
        user = user_service.get_user_info(user_id)

        if not user:
            return jsonify({'error': '유저를 찾을 수 없습니다'}), 404

        # HTML 렌더링 또는 JSON 반환
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(user)

        return render_template('users/detail.html', user=user)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>/currency', methods=['POST'])
@admin_required
def adjust_currency(user_id: int):
    """
    유저 재화 조정 (관리자 전용)
    POST /users/<user_id>/currency
    Body: {
        "amount": int,
        "reason": str
    }
    """
    try:
        data = request.get_json()
        amount = data.get('amount')
        reason = data.get('reason', '관리자 수동 조정')

        # 입력 검증
        if amount is None:
            return jsonify({'error': 'amount 필드가 필요합니다'}), 400

        if not isinstance(amount, int):
            return jsonify({'error': 'amount는 정수여야 합니다'}), 400

        # 서비스 호출
        success = user_service.adjust_user_currency(user_id, amount, reason)

        if not success:
            return jsonify({'error': '재화 조정에 실패했습니다 (잔액 부족 또는 유저 없음)'}), 400

        # 업데이트된 유저 정보 반환
        user = user_service.get_user_info(user_id)
        return jsonify({
            'success': True,
            'user': user
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/stats', methods=['GET'])
@admin_required
def get_statistics():
    """
    유저 통계 조회 (대시보드용)
    GET /users/stats
    """
    try:
        stats = user_service.get_user_statistics()
        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    현재 로그인한 유저 정보 조회
    GET /users/me
    """
    try:
        user_id = session['user_id']
        user = user_service.get_user_info(user_id)

        if not user:
            return jsonify({'error': '유저를 찾을 수 없습니다'}), 404

        return jsonify(user)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
