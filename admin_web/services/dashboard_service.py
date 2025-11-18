"""Dashboard service"""
from admin_web.repositories.database import get_economy_db
from admin_web.repositories.transaction_repository import TransactionRepository


class DashboardService:
    """대시보드 비즈니스 로직"""

    def __init__(self):
        self.transaction_repo = TransactionRepository()

    def get_stats(self) -> dict:
        """전체 통계"""
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 유저 통계
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM users
                WHERE last_active > datetime('now', '-24 hours')
            """)
            active_24h = cursor.fetchone()[0]

            # 현재 휴가 중인 사용자 수
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM vacations
                WHERE date('now') BETWEEN start_date AND end_date
            """)
            on_vacation = cursor.fetchone()[0]

            # 재화 통계
            total_earned = self.transaction_repo.get_total_earned()
            total_spent = self.transaction_repo.get_total_spent()
            total_circulating = total_earned - total_spent

            # 활동량 통계 (PostgreSQL 연동 필요 - Mastodon DB)
            # PostgreSQL이 연동되면 replies_48h와 users_below_threshold를 조회
            replies_48h = 0
            users_below_threshold = 0

            # 경고 통계
            cursor.execute("SELECT COUNT(*) FROM warnings")
            total_warnings = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM warnings
                WHERE timestamp > datetime('now', '-7 days')
            """)
            warnings_this_week = cursor.fetchone()[0]

        return {
            'users': {
                'total': total_users,
                'active_24h': active_24h,
                'on_vacation': on_vacation,
            },
            'currency': {
                'total_circulating': total_circulating,
                'total_earned': total_earned,
                'total_spent': total_spent,
            },
            'activity': {
                'replies_48h': replies_48h,
                'users_below_threshold': users_below_threshold,
            },
            'warnings': {
                'total': total_warnings,
                'this_week': warnings_this_week,
            }
        }
