"""
VacationRepository

vacation 테이블에 대한 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional
from datetime import date, time, datetime

from admin_web.models.vacation import Vacation
from admin_web.utils.datetime_utils import parse_datetime, parse_date, parse_time


class VacationRepository:
    """
    Vacation 데이터 접근을 위한 Repository

    vacation 테이블에 대한 모든 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        VacationRepository를 초기화합니다.

        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """
        Row factory가 설정된 데이터베이스 연결을 가져옵니다.

        Returns:
            SQLite 연결 객체
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_vacation(self, row: sqlite3.Row) -> Vacation:
        """
        데이터베이스 row를 Vacation 모델로 변환합니다.

        Args:
            row: SQLite row 객체

        Returns:
            Vacation 인스턴스
        """
        return Vacation(
            id=row['id'],
            user_id=row['user_id'],
            start_date=parse_date(row['start_date']),
            start_time=parse_time(row['start_time']),
            end_date=parse_date(row['end_date']),
            end_time=parse_time(row['end_time']),
            reason=row['reason'],
            approved=bool(row['approved']),
            registered_by=row['registered_by'],
            created_at=parse_datetime(row['created_at'])
        )

    def create(self, vacation: Vacation) -> Vacation:
        """
        새 휴가를 생성합니다.

        Args:
            vacation: 생성할 Vacation 인스턴스

        Returns:
            ID가 포함된 생성된 휴가
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO vacation (
                user_id, start_date, start_time,
                end_date, end_time, reason,
                approved, registered_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            vacation.user_id,
            vacation.start_date.isoformat() if vacation.start_date else None,
            vacation.start_time.isoformat() if vacation.start_time else None,
            vacation.end_date.isoformat() if vacation.end_date else None,
            vacation.end_time.isoformat() if vacation.end_time else None,
            vacation.reason,
            1 if vacation.approved else 0,
            vacation.registered_by
        ))

        vacation_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return self.find_by_id(vacation_id)

    def find_by_id(self, vacation_id: int) -> Optional[Vacation]:
        """
        ID로 휴가를 조회합니다.

        Args:
            vacation_id: 휴가 ID

        Returns:
            찾은 경우 Vacation, 아니면 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM vacation
            WHERE id = ?
        """, (vacation_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_vacation(row)
        return None

    def find_all(self) -> List[Vacation]:
        """
        모든 휴가를 조회합니다.

        Returns:
            모든 휴가의 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM vacation
            ORDER BY start_date DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_vacation(row) for row in rows]

    def find_by_user(self, user_id: str) -> List[Vacation]:
        """
        특정 유저의 모든 휴가를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저의 휴가 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM vacation
            WHERE user_id = ?
            ORDER BY start_date DESC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_vacation(row) for row in rows]

    def find_by_approved(self, approved: bool) -> List[Vacation]:
        """
        승인 여부별로 휴가를 조회합니다.

        Args:
            approved: 승인 여부

        Returns:
            지정된 승인 상태의 휴가 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM vacation
            WHERE approved = ?
            ORDER BY start_date DESC
        """, (1 if approved else 0,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_vacation(row) for row in rows]

    def find_by_date_range(self, start: date, end: date) -> List[Vacation]:
        """
        날짜 범위로 휴가를 조회합니다.

        시작일 또는 종료일이 주어진 범위에 포함되는 휴가를 모두 조회합니다.

        Args:
            start: 검색 시작일
            end: 검색 종료일

        Returns:
            날짜 범위 내의 휴가 리스트
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM vacation
            WHERE (start_date >= ? AND start_date <= ?)
               OR (end_date >= ? AND end_date <= ?)
               OR (start_date <= ? AND end_date >= ?)
            ORDER BY start_date
        """, (
            start.isoformat(), end.isoformat(),
            start.isoformat(), end.isoformat(),
            start.isoformat(), end.isoformat()
        ))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_vacation(row) for row in rows]

    def count(self) -> int:
        """
        전체 휴가 수를 계산합니다.

        Returns:
            전체 휴가 개수
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count FROM vacation
        """)

        row = cursor.fetchone()
        conn.close()

        return row['count']

    def get_user_vacation_count(self, user_id: str) -> int:
        """
        특정 유저의 휴가 수를 조회합니다.

        Args:
            user_id: 유저의 Mastodon ID

        Returns:
            유저의 휴가 개수
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count FROM vacation
            WHERE user_id = ?
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        return row['count']

    def update_approved(self, vacation_id: int, approved: bool) -> None:
        """
        휴가의 승인 상태를 업데이트합니다.

        Args:
            vacation_id: 휴가 ID
            approved: 승인 여부 (True: 승인, False: 거부)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE vacation
            SET approved = ?
            WHERE id = ?
        """, (1 if approved else 0, vacation_id))

        conn.commit()
        conn.close()

    def delete(self, vacation_id: int) -> bool:
        """
        휴가를 삭제합니다.

        Args:
            vacation_id: 휴가 ID

        Returns:
            삭제 성공 시 True, 실패 시 False
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM vacation
            WHERE id = ?
        """, (vacation_id,))

        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected > 0
