"""
DashboardRepository

대시보드 통계 쿼리를 전담하는 데이터 접근 계층
"""
import sqlite3
from typing import List, Optional

class DashboardRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _execute_scalar(self, query: str, params: tuple = ()) -> int:
        """단일 숫자 값을 반환하는 쿼리 실행 헬퍼"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_total_users(self, system_roles: List[str]) -> int:
        """시스템 계정을 제외한 전체 유저 수"""
        if not system_roles:
            return self._execute_scalar("SELECT COUNT(*) FROM users")
            
        placeholders = ','.join(['?'] * len(system_roles))
        sql = f"SELECT COUNT(*) FROM users WHERE role_name IS NULL OR role_name NOT IN ({placeholders})"
        return self._execute_scalar(sql, tuple(system_roles))

    def get_active_users_24h(self, since: str, system_roles: List[str]) -> int:
        """24시간 내 활동한 유저 수 (시스템 계정 제외)"""
        placeholders = ','.join(['?'] * len(system_roles))
        params = [since] + system_roles
        
        sql = f"""
            SELECT COUNT(*) FROM users 
            WHERE last_active >= ? 
              AND (role_name IS NULL OR role_name NOT IN ({placeholders}))
        """
        return self._execute_scalar(sql, tuple(params))

    def get_total_balance(self, system_roles: List[str]) -> int:
        """전체 유저 보유 재화 총합 (시스템 계정 제외)"""
        placeholders = ','.join(['?'] * len(system_roles))
        sql = f"""
            SELECT SUM(balance) FROM users 
            WHERE role_name IS NULL OR role_name NOT IN ({placeholders})
        """
        # SUM이 NULL일 경우 0 처리 로직은 _execute_scalar 결과가 None이 아니므로 별도 처리 필요할 수 있음
        # 여기서는 간단히 구현
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(system_roles))
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0

    def get_user_stats_risk_count(self, field_name: str, system_roles: List[str]) -> int:
        """특정 위험 유형(고립/편향/회피/미달)에 해당하는 유저 수"""
        # field_name(컬럼명)은 SQL Injection 위험이 있으므로 화이트리스트 검증
        allowed_fields = ['is_isolated', 'is_biased', 'is_avoiding', 'is_inactive']
        if field_name not in allowed_fields:
            return 0
            
        placeholders = ','.join(['?'] * len(system_roles))
        sql = f"""
            SELECT COUNT(*) 
            FROM user_stats s
            JOIN users u ON s.user_id = u.mastodon_id
            WHERE s.{field_name} = 1
              AND (u.role_name IS NULL OR u.role_name NOT IN ({placeholders}))
        """
        return self._execute_scalar(sql, tuple(system_roles))

    def get_total_risk_users_count(self, system_roles: List[str]) -> int:
        """하나라도 위험 요소가 있는 유저 총 수"""
        placeholders = ','.join(['?'] * len(system_roles))
        sql = f"""
            SELECT COUNT(DISTINCT s.user_id) 
            FROM user_stats s
            JOIN users u ON s.user_id = u.mastodon_id
            WHERE (s.is_isolated = 1 OR s.is_biased = 1 OR s.is_avoiding = 1 OR s.is_inactive = 1)
              AND (u.role_name IS NULL OR u.role_name NOT IN ({placeholders}))
        """
        return self._execute_scalar(sql, tuple(system_roles))

    def get_on_vacation_count(self, today: str) -> int:
        """현재 휴가 중인 유저 수"""
        sql = "SELECT COUNT(*) FROM vacation WHERE start_date <= ? AND end_date >= ? AND approved = 1"
        return self._execute_scalar(sql, (today, today))

    def get_scheduled_stories_count(self) -> int:
        """예약 대기 중인 스토리 수"""
        # 테이블명이 story_events라고 가정
        sql = "SELECT COUNT(*) FROM story_events WHERE status = 'pending'"
        return self._execute_scalar(sql)

    def get_scheduled_announcements_count(self) -> int:
        """발송 대기 중인 공지 수"""
        sql = "SELECT COUNT(*) FROM scheduled_posts WHERE status = 'pending' AND post_type = 'announcement'"
        return self._execute_scalar(sql)

    def get_warnings_7d_count(self, since: str) -> int:
        """최근 7일간 발송된 경고 수"""
        sql = "SELECT COUNT(*) FROM warnings WHERE timestamp >= ?"
        return self._execute_scalar(sql, (since,))
