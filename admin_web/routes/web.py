"""Web page routes (HTML)"""
from flask import Blueprint, render_template, request
from admin_web.services.admin_log_service import AdminLogService
from admin_web.services.dashboard_service import DashboardService

web_bp = Blueprint('web', __name__)

# Services
log_service = AdminLogService()
dashboard_service = DashboardService()


@web_bp.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@web_bp.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    try:
        stats = dashboard_service.get_stats()
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        return render_template('errors/500.html', error=str(e)), 500


@web_bp.route('/logs')
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
