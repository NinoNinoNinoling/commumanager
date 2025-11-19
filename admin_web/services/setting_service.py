"""Setting service"""
from typing import List, Optional
from admin_web.models.setting import Setting
from admin_web.repositories.setting_repository import SettingRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository
from admin_web.models.admin_log import AdminLog


class SettingService:
    """설정 비즈니스 로직"""

    def __init__(self):
        self.setting_repo = SettingRepository()
        self.admin_log_repo = AdminLogRepository()

    def get_settings(self) -> List[dict]:
        """전체 설정 조회"""
        settings = self.setting_repo.find_all()
        return [s.to_dict() for s in settings]

    def get_setting(self, key: str) -> Optional[Setting]:
        """설정 조회"""
        return self.setting_repo.find_by_key(key)

    def update_setting(self, key: str, value: str, admin_name: str = None) -> bool:
        """설정 업데이트"""
        success = self.setting_repo.update(key, value)

        # 관리자 로그 생성
        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='update_setting',
                details=f"{key} = {value}",
            )
            self.admin_log_repo.create(log)

        return success
