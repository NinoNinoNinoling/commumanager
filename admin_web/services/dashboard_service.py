"""
DashboardService

대시보드 통계 데이터를 계산하는 비즈니스 로직
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from flask import current_app

from admin_web.constants import SYSTEM_ROLES
from admin_web.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    """
    대시보드 통계 계산을 위한 Service

    직접적인 DB 접근 없이 DashboardRepository를 통해 통계 데이터를 조회합니다.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = current_app.config.get('DATABASE_PATH', 'economy.db')
        else:
            self.db_path = db_path
        
        # Repository 초기화
        self.dashboard_repo = DashboardRepository(self.db_path)

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        대시보드에 표시할 모든 통계를 계산합니다.
        """
        stats = {}
        system_roles_list = list(SYSTEM_ROLES)

        # 1. 전체 유저 (시스템 역할 제외)
        stats['total_users'] = self.dashboard_repo.get_total_users(system_roles_list)

        # 2. 활성 유저 (24시간 내)
        since_24h = (datetime.now() - timedelta(hours=24)).isoformat()
        stats['active_users_24h'] = self.dashboard_repo.get_active_users_24h(since_24h, system_roles_list)

        # 3. 총 재화 (시스템 역할 제외)
        stats['total_balance'] = self.dashboard_repo.get_total_balance(system_roles_list)

        # 4. 위험 유형별 통계
        stats['isolation_risk'] = self.dashboard_repo.get_user_stats_risk_count('is_isolated', system_roles_list)
        stats['bias_risk'] = self.dashboard_repo.get_user_stats_risk_count('is_biased', system_roles_list)
        stats['avoidance_risk'] = self.dashboard_repo.get_user_stats_risk_count('is_avoiding', system_roles_list)
        stats['reply_low_risk'] = self.dashboard_repo.get_user_stats_risk_count('is_inactive', system_roles_list)

        # 위험 감지 유저 총합
        stats['risk_users'] = self.dashboard_repo.get_total_risk_users_count(system_roles_list)

        # 5. 휴식 중 유저 (오늘 날짜 기준)
        today = datetime.now().date().isoformat()
        stats['on_vacation'] = self.dashboard_repo.get_on_vacation_count(today)

        # 6. 예약된 컨텐츠
        stats['scheduled_stories'] = self.dashboard_repo.get_scheduled_stories_count()
        stats['scheduled_announcements'] = self.dashboard_repo.get_scheduled_announcements_count()

        # 7. 최근 경고 발송 (7일 내)
        since_7d = (datetime.now() - timedelta(days=7)).isoformat()
        stats['warnings_7d'] = self.dashboard_repo.get_warnings_7d_count(since_7d)

        return stats
