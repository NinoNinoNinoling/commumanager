"""Warning service"""
from typing import List, Optional
from admin_web.models.warning import Warning
from admin_web.repositories.warning_repository import WarningRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository
from admin_web.models.admin_log import AdminLog


class WarningService:
    """경고 비즈니스 로직"""

    def __init__(self):
        self.warning_repo = WarningRepository()
        self.admin_log_repo = AdminLogRepository()

    def get_warnings(self, page: int = 1, limit: int = 50) -> dict:
        """경고 목록 조회"""
        warnings, total = self.warning_repo.find_all(page, limit)
        total_pages = (total + limit - 1) // limit

        return {
            'warnings': [w.to_dict() for w in warnings],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
            }
        }

    def get_user_warnings(self, user_id: str, page: int = 1, limit: int = 50) -> dict:
        """유저별 경고 조회"""
        warnings, total = self.warning_repo.find_by_user(user_id, page, limit)
        total_pages = (total + limit - 1) // limit

        return {
            'warnings': [w.to_dict() for w in warnings],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
            }
        }

    def create_warning(self, warning_data: dict) -> Warning:
        """경고 생성"""
        # 1. 경고 생성
        warning = Warning(
            id=None,
            user_id=warning_data['user_id'],
            warning_type=warning_data.get('warning_type', 'manual'),
            check_period_hours=warning_data.get('check_period_hours'),
            required_replies=warning_data.get('required_replies'),
            actual_replies=warning_data.get('actual_replies'),
            message=warning_data.get('message'),
            dm_sent=warning_data.get('dm_sent', False),
            admin_name=warning_data.get('admin_name'),
        )
        created_warning = self.warning_repo.create(warning)

        # 2. 관리자 로그 생성
        admin_name = warning_data.get('admin_name')
        if admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='create_warning',
                target_user=warning_data['user_id'],
                details=f"{warning_data.get('warning_type', 'manual')} - {warning_data.get('message', '')}",
            )
            self.admin_log_repo.create(log)

        return created_warning
