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
from admin_web.services.story_event_service import StoryEventService
from admin_web.services.scheduled_announcement_service import ScheduledAnnouncementService
from admin_web.utils.decorators import login_required, admin_required
from admin_web.repositories.database import get_economy_db

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
story_event_service = StoryEventService()
announcement_service = ScheduledAnnouncementService()


@web_bp.route('/')
def index():
    """메인 페이지 - 대시보드 또는 로그인 페이지"""
    if 'user_id' in session:
        # 로그인된 경우 대시보드 표시
        try:
            stats = dashboard_service.get_stats()
            return render_template('dashboard.html', stats=stats)
        except Exception as e:
            return render_template('errors/500.html', error=str(e)), 500
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
            action_type=None  # 액션 필터는 클라이언트 사이드에서 처리
        )

        logs_data = result['logs']
        pagination = result['pagination']

        # 고유 관리자 및 액션 추출
        unique_admins = sorted(set(log['admin_name'] for log in logs_data if log['admin_name']))
        unique_actions = sorted(set(log['action_type'] for log in logs_data if log['action_type']))

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
        if not user:
            return render_template('error.html', error_title="사용자 없음", error_message="사용자를 찾을 수 없습니다."), 404

        transactions_data = user_service.get_user_transactions(mastodon_id, limit=20)
        warnings_data = warning_service.get_warnings(page=1, limit=100, user_id=mastodon_id)
        vacations_data = vacation_service.get_vacations(page=1, limit=100, user_id=mastodon_id)

        return render_template(
            'user_detail.html',
            user=user,
            transactions=transactions_data.get('transactions', []),
            warnings=warnings_data.get('warnings', []),
            vacations=vacations_data.get('vacations', [])
        )
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
        page = int(request.args.get('page', 1))
        user_id = request.args.get('user_id', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        warnings_data = warning_service.get_warnings(
            page=page,
            limit=50,
            user_id=user_id if user_id else None
        )

        # 통계 계산
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 이번 주 경고 수
            cursor.execute("""
                SELECT COUNT(*) FROM warnings
                WHERE timestamp > datetime('now', '-7 days')
            """)
            this_week = cursor.fetchone()[0]

            # 오늘 경고 수
            cursor.execute("""
                SELECT COUNT(*) FROM warnings
                WHERE date(timestamp) = date('now')
            """)
            today = cursor.fetchone()[0]

        stats = {
            'this_week': this_week,
            'today': today
        }

        return render_template(
            'warnings.html',
            warnings=warnings_data.get('warnings', []),
            pagination=warnings_data.get('pagination', {}),
            stats=stats,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to
        )
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500


# ============================================================================
# 휴식 관리
# ============================================================================

@web_bp.route('/vacations')
@login_required
def vacations():
    """휴식 목록 페이지"""
    try:
        page = int(request.args.get('page', 1))
        user_id = request.args.get('user_id', '')
        status = request.args.get('status', '')
        month = request.args.get('month', '')

        vacations_data = vacation_service.get_vacations(
            page=page,
            limit=50,
            user_id=user_id if user_id else None
        )

        # 통계 계산
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 현재 휴식 중인 사용자 수
            cursor.execute("""
                SELECT COUNT(*) FROM vacation
                WHERE date('now') BETWEEN start_date AND end_date
            """)
            active = cursor.fetchone()[0]

            # 이번 달 휴식 신청 수
            cursor.execute("""
                SELECT COUNT(*) FROM vacation
                WHERE strftime('%Y-%m', start_date) = strftime('%Y-%m', 'now')
            """)
            this_month = cursor.fetchone()[0]

        stats = {
            'active': active,
            'this_month': this_month
        }

        return render_template(
            'vacations.html',
            vacations=vacations_data.get('vacations', []),
            pagination=vacations_data.get('pagination', {}),
            stats=stats,
            user_id=user_id,
            status=status,
            month=month
        )
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
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')
        event_type = request.args.get('event_type', '')
        status = request.args.get('status', '')

        events_data = calendar_service.get_events(
            page=page,
            limit=50,
            event_type=event_type if event_type else None
        )

        # 통계 계산
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 진행 중 이벤트 (오늘이 start_date와 end_date 사이)
            cursor.execute("""
                SELECT COUNT(*) FROM calendar_events
                WHERE date('now') BETWEEN date(start_date) AND date(end_date)
            """)
            active = cursor.fetchone()[0]

            # 예정 이벤트 (start_date가 오늘 이후)
            cursor.execute("""
                SELECT COUNT(*) FROM calendar_events
                WHERE date(start_date) > date('now')
            """)
            upcoming = cursor.fetchone()[0]

            # 종료된 이벤트 (end_date가 오늘 이전)
            cursor.execute("""
                SELECT COUNT(*) FROM calendar_events
                WHERE date(end_date) < date('now')
            """)
            completed = cursor.fetchone()[0]

        stats = {
            'active': active,
            'upcoming': upcoming,
            'completed': completed
        }

        return render_template(
            'events.html',
            events=events_data.get('events', []),
            pagination=events_data.get('pagination', {}),
            stats=stats,
            search=search,
            event_type=event_type,
            status=status
        )
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
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')
        is_active_str = request.args.get('is_active', '')
        is_active = None
        if is_active_str:
            is_active = is_active_str.lower() == 'true'

        items_data = item_service.get_items(
            page=page,
            limit=50,
            is_active=is_active
        )

        # 통계 계산
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 활성 아이템 수
            cursor.execute("""
                SELECT COUNT(*) FROM items
                WHERE is_active = 1
            """)
            active = cursor.fetchone()[0]

            # 비활성 아이템 수
            cursor.execute("""
                SELECT COUNT(*) FROM items
                WHERE is_active = 0
            """)
            inactive = cursor.fetchone()[0]

        stats = {
            'active': active,
            'inactive': inactive
        }

        return render_template(
            'items.html',
            items=items_data.get('items', []),
            pagination=items_data.get('pagination', {}),
            stats=stats,
            search=search,
            is_active=is_active_str
        )
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
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')

        settings_data = setting_service.get_settings(
            page=page,
            limit=100,
            search=search if search else None
        )

        return render_template(
            'settings.html',
            settings=settings_data.get('settings', []),
            pagination=settings_data.get('pagination', {}),
            search=search
        )
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500


# ============================================================================
# 스토리 이벤트 관리
# ============================================================================

@web_bp.route('/story-events')
@login_required
def story_events():
    """스토리 이벤트 목록 페이지"""
    try:
        page = int(request.args.get('page', 1))
        status = request.args.get('status', '')

        events_data = story_event_service.get_events(
            page=page,
            limit=50,
            status=status if status else None
        )

        # 통계 계산
        with get_economy_db() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM story_events WHERE status = 'pending'")
            pending = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM story_events WHERE status = 'in_progress'")
            in_progress = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM story_events WHERE status = 'completed'")
            completed = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM story_events WHERE status = 'failed'")
            failed = cursor.fetchone()[0]

        stats = {
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'failed': failed
        }

        return render_template(
            'story_events.html',
            events=events_data.get('events', []),
            pagination=events_data.get('pagination', {}),
            stats=stats,
            status=status
        )
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500


# ============================================================================
# 공지 예약 관리
# ============================================================================

@web_bp.route('/announcements')
@login_required
def announcements():
    """공지 예약 목록 페이지"""
    try:
        page = int(request.args.get('page', 1))
        status = request.args.get('status', '')
        post_type = request.args.get('type', '')

        announcements_data = announcement_service.get_announcements(
            page=page,
            limit=50,
            status=status if status else None,
            post_type=post_type if post_type else None
        )

        # 통계 계산
        with get_economy_db() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM scheduled_posts WHERE status = 'pending'")
            pending = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM scheduled_posts WHERE status = 'published'")
            published = cursor.fetchone()[0]

        stats = {
            'pending': pending,
            'published': published
        }

        return render_template(
            'announcements.html',
            announcements=announcements_data.get('announcements', []),
            pagination=announcements_data.get('pagination', {}),
            stats=stats,
            status=status,
            post_type=post_type
        )
    except Exception as e:
        return render_template('error.html', error_title="오류", error_message=str(e)), 500
