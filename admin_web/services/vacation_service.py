"""
VacationService

Vacation 관련 비즈니스 로직을 처리하는 서비스 계층
"""
from typing import List, Optional, Dict, Any
from datetime import date, time, datetime

from admin_web.models.vacation import Vacation
from admin_web.repositories.vacation_repository import VacationRepository


class VacationService:
    """
    Vacation 비즈니스 로직을 처리하는 Service
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        VacationService를 초기화합니다.
        """
        self.db_path = db_path
        self.vacation_repo = VacationRepository(db_path)

    # 🆕 현재 휴가 중인지 확인하는 메서드 추가 (유저 상세 페이지용)
    def is_user_on_vacation(self, user_id: str) -> bool:
        """
        유저가 현재 승인된 휴가 기간에 있는지 확인합니다.
        
        Args:
            user_id: 유저의 Mastodon ID
            
        Returns:
            현재 휴가 중이면 True
        """
        today = datetime.now().date()
        
        # Repository에 현재 활성 휴가를 조회하는 전용 메서드가 있다고 가정하고 호출합니다.
        # [참고: VacationRepository.is_active_today 메서드를 구현해야 합니다.]
        try:
             # Repository 계층을 통해 현재 활성 휴가 상태 확인
             # approved=1이며 start_date <= today <= end_date 조건을 체크합니다.
             return self.vacation_repo.is_active_today(user_id, today)
        except AttributeError:
             # Repository 메서드가 아직 구현되지 않았을 경우, 모든 휴가를 가져와서 확인합니다 (비효율적이지만 안전함)
             vacations = self.vacation_repo.find_by_user(user_id)
             for v in vacations:
                 if v.approved and v.start_date <= today and v.end_date >= today:
                     return True
             return False

    def create_vacation(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        registered_by: str,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        reason: Optional[str] = None,
        approved: bool = True
    ) -> Dict[str, Any]:
        """휴가를 생성합니다."""
        vacation = Vacation(
            user_id=user_id,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            reason=reason,
            approved=approved,
            registered_by=registered_by
        )
        created_vacation = self.vacation_repo.create(vacation)
        return {'vacation': created_vacation}

    def get_vacation(self, vacation_id: int) -> Optional[Vacation]:
        """ID로 휴가를 조회합니다."""
        return self.vacation_repo.find_by_id(vacation_id)

    def get_user_vacations(self, user_id: str) -> List[Vacation]:
        """특정 유저의 모든 휴가를 조회합니다."""
        return self.vacation_repo.find_by_user(user_id)

    def approve_vacation(self, vacation_id: int, admin_name: str) -> Optional[Vacation]:
        """휴가를 승인합니다."""
        vacation = self.vacation_repo.find_by_id(vacation_id)
        if not vacation: return None
        self.vacation_repo.update_approved(vacation_id, True)
        return self.vacation_repo.find_by_id(vacation_id)

    def reject_vacation(self, vacation_id: int, admin_name: str) -> Optional[Vacation]:
        """휴가를 거부합니다."""
        vacation = self.vacation_repo.find_by_id(vacation_id)
        if not vacation: return None
        self.vacation_repo.update_approved(vacation_id, False)
        return self.vacation_repo.find_by_id(vacation_id)

    def get_vacations_by_date_range(self, start: date, end: date) -> List[Vacation]:
        """날짜 범위로 휴가를 조회합니다."""
        return self.vacation_repo.find_by_date_range(start, end)

    def get_user_vacation_statistics(self, user_id: str) -> Dict[str, Any]:
        """유저의 휴가 통계를 조회합니다."""
        vacations = self.vacation_repo.find_by_user(user_id)
        approved_count = sum(1 for v in vacations if v.approved)
        pending_count = sum(1 for v in vacations if not v.approved)
        
        # 'get_duration_days' 메서드가 Vacation 모델에 있다고 가정
        total_days = sum(v.get_duration_days() for v in vacations) 

        return {
            'total_vacations': len(vacations),
            'approved_vacations': approved_count,
            'pending_vacations': pending_count,
            'total_days': total_days
        }

    def delete_vacation(self, vacation_id: int, admin_name: str) -> bool:
        """휴가를 삭제합니다."""
        vacation = self.vacation_repo.find_by_id(vacation_id)
        if not vacation: return False
        return self.vacation_repo.delete(vacation_id)
