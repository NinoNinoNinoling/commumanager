"""
DashboardService

대시보드 통계 데이터를 계산하는 비즈니스 로직
"""
import sqlite3
from typing import Dict, Any
from datetime import datetime, timedelta


class DashboardService:
    """
    대시보드 통계 계산을 위한 Service

    처리 내용:
    - 유저 통계 (전체, 활성, 위험 유저 등)
    - 활동량 위험 유형별 현황
    - 관리 현황 (휴가, 예약, 경고 등)
    """

    SYSTEM_ROLES = {'Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트'}

    def __init__(self, db_path: str = 'economy.db'):
        """
        DashboardService를 초기화합니다.

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

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        대시보드에 표시할 모든 통계를 계산합니다.

        Returns:
            통계 딕셔너리
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        # 1. 전체 유저 (시스템 역할 제외)
        cursor.execute("""
            SELECT COUNT(*) as count FROM users
            WHERE role_name IS NULL OR role_name = ''
               OR role_name NOT IN ('Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트')
        """)
        stats['total_users'] = cursor.fetchone()['count']

        # 2. 활성 유저 (24시간 내)
        since_24h = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) as count FROM users
            WHERE last_active >= ?
              AND (role_name IS NULL OR role_name = ''
                   OR role_name NOT IN ('Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트'))
        """, (since_24h,))
        stats['active_users_24h'] = cursor.fetchone()['count']

        # 3. 총 재화 (시스템 역할 제외)
        cursor.execute("""
            SELECT COALESCE(SUM(balance), 0) as total FROM users
            WHERE role_name IS NULL OR role_name = ''
               OR role_name NOT IN ('Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트')
        """)
        stats['total_balance'] = cursor.fetchone()['total']

        # 4. 위험 유형별 통계 (user_stats 테이블 사용)
        # 고립 위험
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM user_stats
            WHERE is_isolated = 1
              AND user_id IN (
                  SELECT mastodon_id FROM users
                  WHERE role_name IS NULL OR role_name = ''
                     OR role_name NOT IN ('Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트')
              )
        """)
        stats['isolation_risk'] = cursor.fetchone()['count']

        # 편향 위험
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM user_stats
            WHERE is_biased = 1
              AND user_id IN (
                  SELECT mastodon_id FROM users
                  WHERE role_name IS NULL OR role_name = ''
                     OR role_name NOT IN ('Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트')
              )
        """)
        stats['bias_risk'] = cursor.fetchone()['count']

        # 회피 패턴
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM user_stats
            WHERE is_avoiding = 1
              AND user_id IN (
                  SELECT mastodon_id FROM users
                  WHERE role_name IS NULL OR role_name = ''
                     OR role_name NOT IN ('Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트')
              )
        """)
        stats['avoidance_risk'] = cursor.fetchone()['count']

        # 답글 미달 (최근 48시간 내 활동량 미달 경고 받은 유저 수)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM user_stats
            WHERE is_inactive = 1
              AND user_id IN (
                  SELECT mastodon_id FROM users
                  WHERE role_name IS NULL OR role_name = ''
                     OR role_name NOT IN ('Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트')
              )
        """)
        stats['reply_low_risk'] = cursor.fetchone()['count']

        # 위험 감지 유저 (고립, 편향, 회피, 답글 미달 중 하나라도 해당)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM user_stats
            WHERE (is_isolated = 1 OR is_biased = 1 OR is_avoiding = 1 OR is_inactive = 1)
              AND user_id IN (
                  SELECT mastodon_id FROM users
                  WHERE role_name IS NULL OR role_name = ''
                     OR role_name NOT IN ('Owner', 'Admin', 'Moderator', '봇', '시스템', '테스트')
              )
        """)
        stats['risk_users'] = cursor.fetchone()['count']

        # 5. 휴식 중 유저 (현재 날짜가 휴가 기간에 포함되는 유저)
        today = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM vacation
            WHERE approved = 1
              AND start_date <= ?
              AND end_date >= ?
        """, (today, today))
        stats['on_vacation'] = cursor.fetchone()['count']

        # 6. 예약 스토리 (pending 상태)
        cursor.execute("""
            SELECT COUNT(*) as count FROM story_events
            WHERE status = 'pending'
        """)
        stats['scheduled_stories'] = cursor.fetchone()['count']

        # 7. 예약 공지 (announcement 타입, pending 상태)
        cursor.execute("""
            SELECT COUNT(*) as count FROM scheduled_posts
            WHERE post_type = 'announcement'
              AND status = 'pending'
        """)
        stats['scheduled_announcements'] = cursor.fetchone()['count']

        # 8. 경고 발송 (7일 내)
        since_7d = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) as count FROM warnings
            WHERE timestamp >= ?
        """, (since_7d,))
        stats['warnings_7d'] = cursor.fetchone()['count']

        conn.close()
        return stats
