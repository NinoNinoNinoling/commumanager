"""CalendarRepository"""
import sqlite3
from typing import List, Optional
from datetime import date, time, datetime

from admin_web.models.calendar_event import CalendarEvent
from admin_web.utils.datetime_utils import parse_datetime, parse_date, parse_time


class CalendarRepository:
    """
    일정 이벤트 데이터 접근을 위한 Repository

    calendar_events 테이블에 대한 모든 CRUD 작업을 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        """
        CalendarRepository를 초기화합니다.

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """
        데이터베이스 연결을 생성합니다.

        Returns:
            SQLite 데이터베이스 연결 객체
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_event(self, row: sqlite3.Row) -> CalendarEvent:
        """
        데이터베이스 Row를 CalendarEvent 모델로 변환합니다.

        Args:
            row: 데이터베이스 조회 결과 Row

        Returns:
            변환된 CalendarEvent 객체
        """
        return CalendarEvent(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            event_date=parse_date(row['event_date']),
            start_time=parse_time(row['start_time']),
            end_date=parse_date(row['end_date']),
            end_time=parse_time(row['end_time']),
            event_type=row['event_type'],
            is_global_vacation=bool(row['is_global_vacation']),
            created_by=row['created_by'],
            created_at=parse_datetime(row['created_at']),
            updated_at=parse_datetime(row['updated_at'])
        )

    def create(self, event: CalendarEvent) -> CalendarEvent:
        """
        새 일정 이벤트를 생성합니다.

        Args:
            event: 생성할 CalendarEvent 객체

        Returns:
            생성된 CalendarEvent 객체
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO calendar_events (
                title, description, event_date, start_time, end_date, end_time,
                event_type, is_global_vacation, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.title, event.description, event.event_date.isoformat() if event.event_date else None,
            event.start_time.isoformat() if event.start_time else None,
            event.end_date.isoformat() if event.end_date else None,
            event.end_time.isoformat() if event.end_time else None,
            event.event_type, 1 if event.is_global_vacation else 0, event.created_by
        ))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.find_by_id(event_id)

    def find_by_id(self, event_id: int) -> Optional[CalendarEvent]:
        """
        ID로 일정 이벤트를 조회합니다.

        Args:
            event_id: 이벤트 ID

        Returns:
            조회된 CalendarEvent 객체, 없으면 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_event(row) if row else None

    def find_all(self) -> List[CalendarEvent]:
        """
        모든 일정 이벤트를 조회합니다.

        Returns:
            모든 CalendarEvent 목록 (날짜순 정렬)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calendar_events ORDER BY event_date")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_event(row) for row in rows]

    def find_by_date_range(self, start: date, end: date) -> List[CalendarEvent]:
        """
        특정 기간 내의 일정 이벤트를 조회합니다.

        Args:
            start: 조회 시작 날짜
            end: 조회 종료 날짜

        Returns:
            기간 내 CalendarEvent 목록
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM calendar_events
            WHERE event_date >= ? AND event_date <= ?
            ORDER BY event_date
        """, (start.isoformat(), end.isoformat()))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_event(row) for row in rows]

    def delete(self, event_id: int):
        """
        일정 이벤트를 삭제합니다.

        Args:
            event_id: 삭제할 이벤트 ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()
