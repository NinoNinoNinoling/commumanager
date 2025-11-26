"""
ModerationService

휴식, 경고, 아웃 등 Moderation 관련 기능을 통합 관리하는 서비스 (스텁)
"""
from typing import Dict, Any

class ModerationService:
    def __init__(self, db_path: str = 'economy.db'):
        self.db_path = db_path
        # 이 서비스는 WarningService, VacationService 등에 의존할 것입니다.

    def get_dashboard_moderation_stats(self) -> Dict[str, Any]:
        """대시보드에 필요한 통계 정보를 반환합니다. (스텁)"""
        return {
            'risk_users_count': 0,
            'active_vacations': 0,
            'warnings_7d': 0
        }
