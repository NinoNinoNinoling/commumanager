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

    def create_warning(self, user_id: str, reason: str, count: int, admin_name: str) -> Warning:
        """경고 생성"""
        # 1. 경고 생성
        warning = Warning(
            id=None,
            user_id=user_id,
            reason=reason,
            count=count,
            admin_name=admin_name,
        )
        created_warning = self.warning_repo.create(warning)

        # 2. 관리자 로그 생성
        log = AdminLog(
            id=None,
            admin_name=admin_name,
            action='create_warning',
            target_user=user_id,
            details=f"경고 {count}회 - {reason}",
        )
        self.admin_log_repo.create(log)

        return created_warning
