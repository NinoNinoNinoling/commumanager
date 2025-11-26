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

    휴가 생성, 승인, 거부, 조회 등의 기능을 제공합니다.
    VacationRepository를 사용하여 DB에 접근합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        VacationService를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.vacation_repo = VacationRepository(db_path)

    def is_user_on_vacation(self, user_id: str) -> bool:
        """
        유저가 현재 승인된 휴가 기간에 있는지 확인합니다.
        
        Args:
            user_id: 유저의 Mastodon ID
            
        Returns:
            현재 휴가 중이면 True
        """
        today = datetime.now().date()

        try:
            return self.vacation_repo.is_active_today(user_id, today)
        except AttributeError:
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
        """
        휴가를 생성합니다.

        Args:
            user_id: 유저의 Mastodon ID
            start_date: 시작 날짜
            end_date: 종료 날짜
            registered_by: 등록한 관리자 이름
            start_time: 시작 시간 (선택)
            end_time: 종료 시간 (선택)
            reason: 휴가 사유 (선택)
            approved: 승인 여부 (기본값: True)

        Returns:
            생성된 휴가를 담은 딕셔너리
        """
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
        """
        ID로 휴가를 조회합니다.

        Args:
            vacation_id: 휴가 ID

        Returns:
            찾은 경우 Vacation 객체, 아니면 None
        """
        return self.vacation_repo.find_by_id(vacation_id)

    def get_user_vacations(self, user_id: str) -> List[Vacation]:
        """
        특정 유저의 모든 휴가를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            휴가 리스트
        """
        return self.vacation_repo.find_by_user(user_id)

    def approve_vacation(self, vacation_id: int, admin_name: str) -> Optional[Vacation]:
        """
        휴가를 승인합니다.

        Args:
            vacation_id: 휴가 ID
            admin_name: 승인한 관리자 이름

        Returns:
            승인된 Vacation 객체, 휴가를 찾을 수 없으면 None
        """
        vacation = self.vacation_repo.find_by_id(vacation_id)
        if not vacation:
            return None
        self.vacation_repo.update_approved(vacation_id, True)
        return self.vacation_repo.find_by_id(vacation_id)

    def reject_vacation(self, vacation_id: int, admin_name: str) -> Optional[Vacation]:
        """
        휴가를 거부합니다.

        Args:
            vacation_id: 휴가 ID
            admin_name: 거부한 관리자 이름

        Returns:
            거부된 Vacation 객체, 휴가를 찾을 수 없으면 None
        """
        vacation = self.vacation_repo.find_by_id(vacation_id)
        if not vacation:
            return None
        self.vacation_repo.update_approved(vacation_id, False)
        return self.vacation_repo.find_by_id(vacation_id)

    def get_vacations_by_date_range(self, start: date, end: date) -> List[Vacation]:
        """
        날짜 범위로 휴가를 조회합니다.

        Args:
            start: 시작 날짜
            end: 종료 날짜

        Returns:
            해당 범위에 포함되는 휴가 리스트
        """
        return self.vacation_repo.find_by_date_range(start, end)

    def get_user_vacation_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        유저의 휴가 통계를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            휴가 통계 딕셔너리 (total_vacations, approved_vacations, pending_vacations, total_days)
        """
        vacations = self.vacation_repo.find_by_user(user_id)
        approved_count = sum(1 for v in vacations if v.approved)
        pending_count = sum(1 for v in vacations if not v.approved)
        total_days = sum(v.get_duration_days() for v in vacations) 

        return {
            'total_vacations': len(vacations),
            'approved_vacations': approved_count,
            'pending_vacations': pending_count,
            'total_days': total_days
        }

    def delete_vacation(self, vacation_id: int, admin_name: str) -> bool:
        """
        휴가를 삭제합니다.

        Args:
            vacation_id: 휴가 ID
            admin_name: 삭제한 관리자 이름

        Returns:
            삭제 성공 여부
        """
        vacation = self.vacation_repo.find_by_id(vacation_id)
        if not vacation:
            return False
        return self.vacation_repo.delete(vacation_id)
