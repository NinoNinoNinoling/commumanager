"""Vacation service"""
from typing import List, Optional
from admin_web.models.vacation import Vacation
from admin_web.repositories.vacation_repository import VacationRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository
from admin_web.models.admin_log import AdminLog


class VacationService:
    """휴가 비즈니스 로직"""

    def __init__(self):
        self.vacation_repo = VacationRepository()
        self.admin_log_repo = AdminLogRepository()

    def get_vacations(self, page: int = 1, limit: int = 50) -> dict:
        """휴가 목록 조회"""
        vacations, total = self.vacation_repo.find_all(page, limit)
        total_pages = (total + limit - 1) // limit

        return {
            'vacations': [v.to_dict() for v in vacations],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
            }
        }

    def get_user_vacations(self, user_id: str) -> List[dict]:
        """유저별 휴가 조회"""
        vacations = self.vacation_repo.find_by_user(user_id)
        return [v.to_dict() for v in vacations]

    def create_vacation(self, user_id: str, start_date: str, end_date: str,
                        start_time: str = None, end_time: str = None,
                        reason: str = None, admin_name: str = None) -> Vacation:
        """휴가 생성"""
        # 1. 휴가 생성
        vacation = Vacation(
            id=None,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
        )
        created_vacation = self.vacation_repo.create(vacation)

        # 2. 관리자 로그 생성 (관리자가 생성한 경우)
        if admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action='create_vacation',
                target_user=user_id,
                details=f"{start_date} ~ {end_date}",
            )
            self.admin_log_repo.create(log)

        return created_vacation

    def delete_vacation(self, vacation_id: int, admin_name: str = None) -> bool:
        """휴가 삭제"""
        success = self.vacation_repo.delete(vacation_id)

        # 관리자 로그 생성 (관리자가 삭제한 경우)
        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action='delete_vacation',
                details=f"vacation_id: {vacation_id}",
            )
            self.admin_log_repo.create(log)

        return success
