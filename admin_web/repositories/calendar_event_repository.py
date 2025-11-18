"""Calendar Event repository"""
from typing import List, Optional
from admin_web.models.calendar_event import CalendarEvent
from admin_web.repositories.database import get_economy_db


class CalendarEventRepository:
    """캘린더 이벤트 데이터 저장소"""

    @staticmethod
    def find_all(page: int = 1, limit: int = 50, event_type: str = None) -> tuple[List[CalendarEvent], int]:
        """이벤트 목록 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # WHERE 조건
            where_clause = "event_type = ?" if event_type else "1=1"
            params = [event_type] if event_type else []

            # 전체 개수
            cursor.execute(f"SELECT COUNT(*) FROM calendar_events WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            # 페이징
            offset = (page - 1) * limit
            cursor.execute(f"""
                SELECT * FROM calendar_events
                WHERE {where_clause}
                ORDER BY start_date DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])

            events = [CalendarEvent(**dict(row)) for row in cursor.fetchall()]
            return events, total

    @staticmethod
    def find_by_id(event_id: int) -> Optional[CalendarEvent]:
        """ID로 이벤트 조회"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                return CalendarEvent(**dict(row))
            return None

    @staticmethod
    def create(event: CalendarEvent) -> CalendarEvent:
        """이벤트 생성"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calendar_events (title, description, event_type, start_date, end_date, start_time, end_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (event.title, event.description, event.event_type,
                  event.start_date, event.end_date, event.start_time, event.end_time))
            conn.commit()

            # 생성된 ID로 조회
            event_id = cursor.lastrowid
            return CalendarEventRepository.find_by_id(event_id)

    @staticmethod
    def update(event: CalendarEvent) -> bool:
        """이벤트 수정"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE calendar_events
                SET title = ?, description = ?, event_type = ?,
                    start_date = ?, end_date = ?, start_time = ?, end_time = ?
                WHERE id = ?
            """, (event.title, event.description, event.event_type,
                  event.start_date, event.end_date, event.start_time, event.end_time, event.id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(event_id: int) -> bool:
        """이벤트 삭제"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0
