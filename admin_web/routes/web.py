from flask import Blueprint, render_template, request, jsonify
from admin_web.repositories.user_repository import UserRepository
from admin_web.services.transaction_service import TransactionService
from admin_web.services.warning_service import WarningService
from admin_web.services.vacation_service import VacationService
from admin_web.services.moderation_service import ModerationService

web = Blueprint('web', __name__)

user_repo = UserRepository()
transaction_service = TransactionService()
warning_service = WarningService()
vacation_service = VacationService()
moderation_service = ModerationService()

@web.route('/')
def dashboard():
    """관리자 대시보드 메인 페이지"""
    stats = user_repo.get_dashboard_stats()
    warning_stats = warning_service.get_dashboard_warning_stats()
    moderation_stats = moderation_service.get_dashboard_moderation_stats()
    
    # 휴가 중인 유저 수 계산 (유지)
    on_vacation_count = moderation_service.get_vacation_count()

    return render_template(
        'dashboard.html',
        stats=stats,
        warning_stats=warning_stats,
        moderation_stats=moderation_stats,
        on_vacation_count=on_vacation_count
    )

@web.route('/users')
def users():
    """유저 목록 페이지 (재화 관리)"""
    users_list = user_repo.find_all_users_with_stats()
    return render_template(
        'users.html',
        users=users_list,
        current_tab='재화 관리'
    )

@web.route('/users/monitoring')
def users_monitoring():
    """유저 목록 페이지 (활동량 모니터링)"""
    users_list = user_repo.find_risky_users() 
    return render_template(
        'users.html',
        users=users_list,
        current_tab='활동량 모니터링'
    )

@web.route('/users/vacation')
def users_vacation():
    """유저 목록 페이지 (휴식 현황)"""
    users_list = user_repo.find_all_users_with_stats() 
    return render_template(
        'users.html',
        users=users_list,
        current_tab='휴식 현황'
    )

@web.route('/users/detail/<user_id>')
def user_detail(user_id):
    """특정 유저 상세 정보 및 재화/경고 내역"""
    user = user_repo.find_by_mastodon_id(user_id)
    if not user:
        user = user_repo.find_by_id(user_id)
        if not user:
             return "User not found", 404

    # 1. 재화 내역 로드
    transactions = transaction_service.get_user_transactions(user.mastodon_id)

    # 2. 경고 내역 로드 (롤백된 로직)
    warnings = warning_service.get_user_warnings(user.mastodon_id)

    # 3. 휴가 상태 확인 (유지)
    is_on_vacation = vacation_service.is_user_on_vacation(user.mastodon_id)


    return render_template(
        'user_detail.html',
        user=user,
        transactions=transactions,
        warnings=warnings,  # 경고 내역 전달
        is_on_vacation=is_on_vacation
    )

@web.route('/api/v1/users/<user_id>/balance', methods=['POST'])
def api_adjust_balance(user_id):
    data = request.json
    amount = data.get('amount')
    description = data.get('description')

    if not amount or not description:
        return jsonify({'error': 'Amount and description are required'}), 400

    try:
        transaction = transaction_service.create_transaction(
            user_id=user_id,
            amount=int(amount),
            description=description,
            category='admin_adjustment'
        )
        return jsonify({'message': 'Balance adjusted successfully', 'transaction': transaction}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web.route('/api/v1/warnings/send', methods=['POST'])
def api_send_warning():
    data = request.json
    user_id = data.get('user_id')
    warning_type = data.get('warning_type')

    if not user_id or not warning_type:
        return jsonify({'error': 'User ID and warning type are required'}), 400

    try:
        warning = warning_service.create_warning_from_ui(user_id, warning_type)
        return jsonify({'message': 'Warning sent successfully', 'warning': warning}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
