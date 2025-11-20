"""Vacation repository"""
from typing import List, Optional
from admin_web.models.vacation import Vacation
from admin_web.repositories.database import get_economy_db


class VacationRepository:
    """휴가 데이터 저장소"""

    @staticmethod
    def find_all(page: int = 1, limit: int = 50) -> tuple[List[Vacation], int]:
        """휴가 목록 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 전체 개수
            cursor.execute("SELECT COUNT(*) FROM vacation")
            total = cursor.fetchone()[0]

            # 페이징
            offset = (page - 1) * limit
            cursor.execute("""
                SELECT * FROM vacation
                ORDER BY start_date DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            vacation = [Vacation(**dict(row)) for row in cursor.fetchall()]
            return vacation, total

    @staticmethod
    def find_by_user(user_id: str) -> List[Vacation]:
        """유저별 휴가 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM vacation
                WHERE user_id = ?
                ORDER BY start_date DESC
            """, (user_id,))
            return [Vacation(**dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def create(vacation: Vacation) -> Vacation:
        """휴가 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vacation (user_id, start_date, end_date, start_time, end_time, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (vacation.user_id, vacation.start_date, vacation.end_date,
                  vacation.start_time, vacation.end_time, vacation.reason))
            conn.commit()

            # 생성된 ID로 조회
            vacation_id = cursor.lastrowid
            cursor.execute("SELECT * FROM vacation WHERE id = ?", (vacation_id,))
            row = cursor.fetchone()
            return Vacation(**dict(row))

    @staticmethod
    def delete(vacation_id: int) -> bool:
        """휴가 삭제"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vacation WHERE id = ?", (vacation_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def is_on_vacation(user_id: str) -> bool:
        """휴가 중인지 확인"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM vacation
                WHERE user_id = ?
                AND date('now') BETWEEN date(start_date) AND date(end_date)
            """, (user_id,))
            return cursor.fetchone()[0] > 0

    @staticmethod
    def count_active() -> int:
        """현재 휴가 중인 유저 수"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM vacation
                WHERE date('now') BETWEEN date(start_date) AND date(end_date)
            """)
            return cursor.fetchone()[0]

    @staticmethod
    def count_active_vacation() -> int:
        """현재 휴가 중인 유저 수 (alias for count_active)"""
        return VacationRepository.count_active()

    @staticmethod
    def is_user_on_vacation(mastodon_id: str) -> bool:
        """휴가 중인지 확인 (alias for is_on_vacation)"""
        return VacationRepository.is_on_vacation(mastodon_id)
