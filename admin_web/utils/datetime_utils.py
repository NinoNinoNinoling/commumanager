"""
Datetime 유틸리티 함수
"""
import logging
from datetime import datetime, date, time
from typing import Optional, Any

logger = logging = logging.getLogger(__name__)

def parse_datetime(value: Any) -> Optional[datetime]:
    """
    다양한 형태의 값으로부터 datetime 객체를 파싱합니다.
    Args:
        value: 파싱할 값. str (ISO 형식), datetime 객체, 또는 None일 수 있습니다.
    Returns:
        Optional[datetime]: 파싱된 datetime 객체, 또는 None.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Try ISO format first
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass # Fall through to other formats

        # Try common SQLite/DB formats
        formats = [
            '%Y-%m-%d %H:%M:%S.%f', # YYYY-MM-DD HH:MM:SS.ffffff
            '%Y-%m-%d %H:%M:%S',   # YYYY-MM-DD HH:MM:SS
            '%Y-%m-%dT%H:%M:%S.%f', # ISO format without Z (e.g. from Python's isoformat())
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d'
        ]
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass # Try next format
        
        logger.warning(f"parse_datetime: Failed to parse string '{value}' to datetime.")
        return None
    return None

def parse_date(value: Any) -> Optional[date]:
    """
    다양한 형태의 값으로부터 date 객체를 파싱합니다.
    Args:
        value: 파싱할 값. str (ISO 형식), date 객체, 또는 None일 수 있습니다.
    Returns:
        Optional[date]: 파싱된 date 객체, 또는 None.
    """
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"parse_date: Failed to parse string '{value}' to date.")
                return None
    return None

def parse_time(value: Any) -> Optional[time]:
    """
    다양한 형태의 값으로부터 time 객체를 파싱합니다.
    Args:
        value: 파싱할 값. str (ISO 형식), time 객체, 또는 None일 수 있습니다.
    Returns:
        Optional[time]: 파싱된 time 객체, 또는 None.
    """
    if value is None:
        return None
    if isinstance(value, time):
        return value
    if isinstance(value, str):
        try:
            # Full ISO format for time includes microseconds
            return time.fromisoformat(value)
        except ValueError:
            # Try to parse without microseconds or just HH:MM:SS
            try:
                return datetime.strptime(value, '%H:%M:%S').time()
            except ValueError:
                logger.warning(f"parse_time: Failed to parse string '{value}' to time.")
                return None
    return None
