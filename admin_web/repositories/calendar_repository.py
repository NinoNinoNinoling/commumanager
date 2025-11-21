"""CalendarRepository"""
import sqlite3
from typing import List, Optional
from datetime import date, time, datetime

from admin_web.models.calendar_event import CalendarEvent


class CalendarRepository:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_event(self, row: sqlite3.Row) -> CalendarEvent:
        return CalendarEvent(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            event_date=date.fromisoformat(row['event_date']) if row['event_date'] else None,
            start_time=time.fromisoformat(row['start_time']) if row['start_time'] else None,
            end_date=date.fromisoformat(row['end_date']) if row['end_date'] else None,
            end_time=time.fromisoformat(row['end_time']) if row['end_time'] else None,
            event_type=row['event_type'],
            is_global_vacation=bool(row['is_global_vacation']),
            created_by=row['created_by'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

    def create(self, event: CalendarEvent) -> CalendarEvent:
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
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_event(row) if row else None

    def find_all(self) -> List[CalendarEvent]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calendar_events ORDER BY event_date")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_event(row) for row in rows]

    def find_by_date_range(self, start: date, end: date) -> List[CalendarEvent]:
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
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()
