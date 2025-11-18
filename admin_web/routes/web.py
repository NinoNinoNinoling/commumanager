"""Web page routes (HTML)"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from admin_web.services.admin_log_service import AdminLogService
from admin_web.services.dashboard_service import DashboardService
from admin_web.services.user_service import UserService
from admin_web.services.warning_service import WarningService
from admin_web.services.vacation_service import VacationService
from admin_web.services.calendar_service import CalendarService
from admin_web.services.item_service import ItemService
from admin_web.services.setting_service import SettingService
from admin_web.utils.decorators import login_required, admin_required

web_bp = Blueprint('web', __name__)

# Services
log_service = AdminLogService()
dashboard_service = DashboardService()
user_service = UserService()
warning_service = WarningService()
vacation_service = VacationService()
calendar_service = CalendarService()
item_service = ItemService()
setting_service = SettingService()


@web_bp.route('/')
def index():
    """메인 페이지 - 로그인 페이지로 리다이렉트"""
    if 'user_id' in session:
        return redirect(url_for('web.dashboard'))
    return redirect(url_for('auth.login'))


@web_bp.route('/dashboard')
@login_required
def dashboard():
    """대시보드 페이지"""
    try:
        stats = dashboard_service.get_stats()
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        return render_template('errors/500.html', error=str(e)), 500


@web_bp.route('/logs')
@login_required
def logs():
    """로그 뷰어 페이지"""
    try:
        # 쿼리 파라미터
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        admin_name = request.args.get('admin_name', '')
        actions_str = request.args.get('actions', '')

        # 선택된 액션들
        selected_actions = [a.strip() for a in actions_str.split(',') if a.strip()]

        # 로그 조회
        result = log_service.get_logs(
            page=page,
            limit=limit,
            admin_name=admin_name if admin_name else None,
            action=None  # 액션 필터는 클라이언트 사이드에서 처리
        )

        logs_data = result['logs']
        pagination = result['pagination']

        # 고유 관리자 및 액션 추출
        unique_admins = sorted(set(log['admin_name'] for log in logs_data if log['admin_name']))
        unique_actions = sorted(set(log['action'] for log in logs_data if log['action']))

        # 액션 타입별 색상
        action_colors = {
            'create_warning': '#f48771',
            'create_vacation': '#4fc1ff',
            'delete_vacation': '#f48771',
            'create_event': '#b5cea8',
            'update_event': '#dcdcaa',
            'delete_event': '#f48771',
            'create_item': '#b5cea8',
            'update_item': '#dcdcaa',
            'delete_item': '#f48771',
            'update_setting': '#c586c0',
            'adjust_balance': '#4ec9b0',
            'change_role': '#569cd6',
        }

        return render_template(
            'logs.html',
            logs=logs_data,
            pagination=pagination,
            unique_admins=unique_admins,
            unique_actions=unique_actions,
            selected_admin=admin_name,
            selected_actions=selected_actions,
            action_colors=action_colors
        )
    except Exception as e:
        return render_template('errors/500.html', error=str(e)), 500


# ============================================================================
# 사용자 관리
# ============================================================================

@web_bp.route('/users')
@login_required
def users():
    """사용자 목록 페이지"""
    try:
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')

        users_data = user_service.get_users(page=page, search=search)
        return render_template('users.html', users=users_data['users'], pagination=users_data.get('pagination'))
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500


@web_bp.route('/users/<mastodon_id>')
@login_required
def user_detail(mastodon_id):
    """사용자 상세 페이지"""
    try:
        user = user_service.get_user(mastodon_id)
        transactions = user_service.get_user_transactions(mastodon_id, limit=20)
        warnings = warning_service.get_user_warnings(mastodon_id)

        return render_template('user_detail.html', user=user, transactions=transactions, warnings=warnings)
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500


# ============================================================================
# 경고 관리
# ============================================================================

@web_bp.route('/warnings')
@login_required
def warnings():
    """경고 목록 페이지"""
    try:
        warnings_data = warning_service.get_warnings(limit=100)
        return render_template('warnings.html', warnings=warnings_data)
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500


# ============================================================================
# 휴가 관리
# ============================================================================

@web_bp.route('/vacations')
@login_required
def vacations():
    """휴가 목록 페이지"""
    try:
        vacations_data = vacation_service.get_vacations(limit=100)
        return render_template('vacations.html', vacations=vacations_data)
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500


# ============================================================================
# 이벤트/일정 관리
# ============================================================================

@web_bp.route('/events')
@login_required
def events():
    """이벤트 목록 페이지"""
    try:
        events_data = calendar_service.get_events(limit=100)
        return render_template('events.html', events=events_data)
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500


# ============================================================================
# 아이템/상점 관리
# ============================================================================

@web_bp.route('/items')
@login_required
def items():
    """아이템 목록 페이지"""
    try:
        items_data = item_service.get_items()
        return render_template('items.html', items=items_data)
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500


# ============================================================================
# 시스템 설정
# ============================================================================

@web_bp.route('/settings')
@login_required
def settings():
    """시스템 설정 페이지"""
    try:
        settings_data = setting_service.get_all_settings()
        return render_template('settings.html', settings=settings_data)
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500
