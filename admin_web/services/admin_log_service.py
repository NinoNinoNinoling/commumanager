"""Admin Log service"""
from typing import List
from admin_web.models.admin_log import AdminLog
from admin_web.repositories.admin_log_repository import AdminLogRepository


class AdminLogService:
    """관리자 로그 비즈니스 로직"""

    def __init__(self):
        self.log_repo = AdminLogRepository()

    def get_logs(self, page: int = 1, limit: int = 50,
                 admin_name: str = None, action: str = None) -> dict:
        """로그 목록 조회"""
        logs, total = self.log_repo.find_all(page, limit, admin_name, action)
        total_pages = (total + limit - 1) // limit

        return {
            'logs': [log.to_dict() for log in logs],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
            }
        }
