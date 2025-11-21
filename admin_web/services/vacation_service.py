"""
VacationService

Vacation 관련 비즈니스 로직을 처리하는 서비스 계층
"""
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import date, time

from admin_web.models.vacation import Vacation
from admin_web.repositories.vacation_repository import VacationRepository


class VacationService:
    """
    Vacation 비즈니스 로직을 처리하는 Service

    VacationRepository를 사용하여 휴가 생성, 조회, 승인/거부,
    삭제 등의 비즈니스 로직을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        VacationService를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.vacation_repo = VacationRepository(db_path)

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
            start_date: 휴가 시작일
            end_date: 휴가 종료일
            registered_by: 등록자 이름
            start_time: 휴가 시작 시간 (선택)
            end_time: 휴가 종료 시간 (선택)
            reason: 휴가 사유 (선택)
            approved: 승인 여부 (기본값: True)

        Returns:
            생성된 휴가 정보를 담은 딕셔너리
        """
        # Vacation 생성
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

        # Repository를 통해 생성
        created_vacation = self.vacation_repo.create(vacation)

        return {
            'vacation': created_vacation
        }

    def get_vacation(self, vacation_id: int) -> Optional[Vacation]:
        """
        ID로 휴가를 조회합니다.

        Args:
            vacation_id: 휴가 ID

        Returns:
            찾은 경우 Vacation, 아니면 None
        """
        return self.vacation_repo.find_by_id(vacation_id)

    def get_user_vacations(self, user_id: str) -> List[Vacation]:
        """
        특정 유저의 모든 휴가를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저의 휴가 리스트
        """
        return self.vacation_repo.find_by_user(user_id)

    def approve_vacation(self, vacation_id: int, admin_name: str) -> Optional[Vacation]:
        """
        휴가를 승인합니다.

        Args:
            vacation_id: 휴가 ID
            admin_name: 승인하는 관리자 이름

        Returns:
            승인된 Vacation, 찾지 못한 경우 None
        """
        # 휴가 존재 확인
        vacation = self.vacation_repo.find_by_id(vacation_id)
        if not vacation:
            return None

        # 승인 상태 업데이트
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE vacation
            SET approved = 1
            WHERE id = ?
        """, (vacation_id,))

        conn.commit()
        conn.close()

        return self.vacation_repo.find_by_id(vacation_id)

    def reject_vacation(self, vacation_id: int, admin_name: str) -> Optional[Vacation]:
        """
        휴가를 거부합니다.

        Args:
            vacation_id: 휴가 ID
            admin_name: 거부하는 관리자 이름

        Returns:
            거부된 Vacation, 찾지 못한 경우 None
        """
        # 휴가 존재 확인
        vacation = self.vacation_repo.find_by_id(vacation_id)
        if not vacation:
            return None

        # 거부 상태 업데이트
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE vacation
            SET approved = 0
            WHERE id = ?
        """, (vacation_id,))

        conn.commit()
        conn.close()

        return self.vacation_repo.find_by_id(vacation_id)

    def get_vacations_by_date_range(
        self,
        start: date,
        end: date
    ) -> List[Vacation]:
        """
        날짜 범위로 휴가를 조회합니다.

        Args:
            start: 시작일
            end: 종료일

        Returns:
            날짜 범위에 해당하는 휴가 리스트
        """
        return self.vacation_repo.find_by_date_range(start, end)

    def get_user_vacation_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        유저의 휴가 통계를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            통계 정보 딕셔너리:
            - total_vacations: 총 휴가 수
            - approved_vacations: 승인된 휴가 수
            - pending_vacations: 미승인 휴가 수
            - total_days: 총 휴가 일수
        """
        # 유저의 모든 휴가 조회
        vacations = self.vacation_repo.find_by_user(user_id)

        # 승인/미승인 카운트
        approved_count = sum(1 for v in vacations if v.approved)
        pending_count = sum(1 for v in vacations if not v.approved)

        # 총 일수 계산
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
            admin_name: 삭제하는 관리자 이름

        Returns:
            삭제 성공 시 True, 찾지 못한 경우 False
        """
        # 휴가 존재 확인
        vacation = self.vacation_repo.find_by_id(vacation_id)
        if not vacation:
            return False

        # 삭제
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM vacation
            WHERE id = ?
        """, (vacation_id,))

        conn.commit()
        conn.close()

        return True
