"""API routes"""
from flask import Blueprint, current_app
from admin_web.controllers.dashboard_controller import DashboardController
from admin_web.controllers.user_controller import UserController
from admin_web.controllers.warning_controller import WarningController
from admin_web.controllers.vacation_controller import VacationController
from admin_web.controllers.calendar_controller import CalendarController
from admin_web.controllers.item_controller import ItemController
from admin_web.controllers.setting_controller import SettingController
from admin_web.controllers.admin_log_controller import AdminLogController
from admin_web.controllers.story_event_controller import StoryEventController
from admin_web.controllers.scheduled_announcement_controller import ScheduledAnnouncementController

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def get_dashboard_controller():
    """대시보드 컨트롤러 인스턴스 가져오기"""
    return DashboardController()


def get_user_controller():
    """사용자 컨트롤러 인스턴스 가져오기"""
    return UserController()


def get_warning_controller():
    """경고 컨트롤러 인스턴스 가져오기"""
    return WarningController()


def get_vacation_controller():
    """휴가 컨트롤러 인스턴스 가져오기"""
    return VacationController()


def get_calendar_controller():
    """일정 컨트롤러 인스턴스 가져오기"""
    return CalendarController()


def get_item_controller():
    """아이템 컨트롤러 인스턴스 가져오기"""
    return ItemController()


def get_setting_controller():
    """설정 컨트롤러 인스턴스 가져오기"""
    return SettingController()


def get_admin_log_controller():
    """관리자 로그 컨트롤러 인스턴스 가져오기"""
    return AdminLogController()


def get_story_controller():
    """스토리 이벤트 컨트롤러 인스턴스 가져오기"""
    return StoryEventController()


def get_announcement_controller():
    """공지 예약 컨트롤러 인스턴스 가져오기"""
    return ScheduledAnnouncementController()


# Dashboard
@api_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """대시보드 통계"""
    return get_dashboard_controller().get_stats()


# Users
@api_bp.route('/users', methods=['GET'])
def get_users():
    """유저 목록"""
    return get_user_controller().get_users()


@api_bp.route('/users/<mastodon_id>', methods=['GET'])
def get_user(mastodon_id):
    """유저 상세"""
    return get_user_controller().get_user(mastodon_id)


@api_bp.route('/users/<mastodon_id>/role', methods=['PATCH'])
def update_user_role(mastodon_id):
    """역할 변경"""
    return get_user_controller().update_role(mastodon_id)


# Transactions
@api_bp.route('/transactions/adjust', methods=['POST'])
def adjust_balance():
    """재화 조정"""
    return get_user_controller().adjust_balance()


@api_bp.route('/users/<mastodon_id>/transactions', methods=['GET'])
def get_user_transactions(mastodon_id):
    """유저별 거래 내역"""
    return get_user_controller().get_transactions(mastodon_id)


# Warnings
@api_bp.route('/warnings', methods=['GET'])
def get_warnings():
    """경고 목록"""
    return get_warning_controller().get_warnings()


@api_bp.route('/warnings', methods=['POST'])
def create_warning():
    """경고 생성"""
    return get_warning_controller().create_warning()


@api_bp.route('/users/<mastodon_id>/warnings', methods=['GET'])
def get_user_warnings(mastodon_id):
    """유저별 경고"""
    return get_warning_controller().get_user_warnings(mastodon_id)


# Vacations
@api_bp.route('/vacations', methods=['GET'])
def get_vacations():
    """휴가 목록"""
    return get_vacation_controller().get_vacations()


@api_bp.route('/vacations', methods=['POST'])
def create_vacation():
    """휴가 생성"""
    return get_vacation_controller().create_vacation()


@api_bp.route('/vacations/<int:vacation_id>', methods=['DELETE'])
def delete_vacation(vacation_id):
    """휴가 삭제"""
    return get_vacation_controller().delete_vacation(vacation_id)


# Calendar Events
@api_bp.route('/calendar/events', methods=['GET'])
def get_events():
    """이벤트 목록"""
    return get_calendar_controller().get_events()


@api_bp.route('/calendar/events', methods=['POST'])
def create_event():
    """이벤트 생성"""
    return get_calendar_controller().create_event()


@api_bp.route('/calendar/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """이벤트 수정"""
    return get_calendar_controller().update_event(event_id)


@api_bp.route('/calendar/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """이벤트 삭제"""
    return get_calendar_controller().delete_event(event_id)


# Items
@api_bp.route('/items', methods=['GET'])
def get_items():
    """아이템 목록"""
    return get_item_controller().get_items()


@api_bp.route('/items', methods=['POST'])
def create_item():
    """아이템 생성"""
    return get_item_controller().create_item()


@api_bp.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """아이템 수정"""
    return get_item_controller().update_item(item_id)


@api_bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """아이템 삭제"""
    return get_item_controller().delete_item(item_id)


# Settings
@api_bp.route('/settings', methods=['GET'])
def get_settings():
    """설정 조회"""
    return get_setting_controller().get_settings()


@api_bp.route('/settings/<key>', methods=['PUT'])
def update_setting(key):
    """설정 업데이트"""
    return get_setting_controller().update_setting(key)


# Admin Logs
@api_bp.route('/admin-logs', methods=['GET'])
def get_admin_logs():
    """관리자 로그"""
    return get_admin_log_controller().get_logs()


# Story Events
@api_bp.route('/story-events', methods=['GET'])
def get_story_events():
    """스토리 이벤트 목록"""
    return get_story_controller().get_events()


@api_bp.route('/story-events/<int:event_id>', methods=['GET'])
def get_story_event(event_id):
    """스토리 이벤트 상세"""
    return get_story_controller().get_event(event_id)


@api_bp.route('/story-events', methods=['POST'])
def create_story_event():
    """스토리 이벤트 생성"""
    return get_story_controller().create_event()


@api_bp.route('/story-events/<int:event_id>', methods=['PUT'])
def update_story_event(event_id):
    """스토리 이벤트 수정"""
    return get_story_controller().update_event(event_id)


@api_bp.route('/story-events/<int:event_id>', methods=['DELETE'])
def delete_story_event(event_id):
    """스토리 이벤트 삭제"""
    return get_story_controller().delete_event(event_id)


@api_bp.route('/story-events/<int:event_id>/posts', methods=['POST'])
def add_story_posts(event_id):
    """스토리 포스트 추가"""
    return get_story_controller().add_posts(event_id)


@api_bp.route('/story-posts/<int:post_id>', methods=['PUT'])
def update_story_post(post_id):
    """스토리 포스트 수정"""
    return get_story_controller().update_post(post_id)


@api_bp.route('/story-posts/<int:post_id>', methods=['DELETE'])
def delete_story_post(post_id):
    """스토리 포스트 삭제"""
    return get_story_controller().delete_post(post_id)


@api_bp.route('/story-events/bulk-upload', methods=['POST'])
def bulk_upload_story_events():
    """스토리 이벤트 엑셀 일괄 업로드"""
    return get_story_controller().bulk_upload_excel()


# Scheduled Announcements
@api_bp.route('/announcements', methods=['GET'])
def get_announcements():
    """공지 목록"""
    return get_announcement_controller().get_announcements()


@api_bp.route('/announcements/<int:announcement_id>', methods=['GET'])
def get_announcement(announcement_id):
    """공지 상세"""
    return get_announcement_controller().get_announcement(announcement_id)


@api_bp.route('/announcements', methods=['POST'])
def create_announcement():
    """공지 생성"""
    return get_announcement_controller().create_announcement()


@api_bp.route('/announcements/<int:announcement_id>', methods=['PUT'])
def update_announcement(announcement_id):
    """공지 수정"""
    return get_announcement_controller().update_announcement(announcement_id)


@api_bp.route('/announcements/<int:announcement_id>', methods=['DELETE'])
def delete_announcement(announcement_id):
    """공지 삭제"""
    return get_announcement_controller().delete_announcement(announcement_id)
