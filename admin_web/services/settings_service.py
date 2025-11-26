"""
SettingsService
"""
from typing import List, Dict, Any
from flask import current_app
from admin_web.repositories.settings_repository import SettingsRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository

class SettingsService:
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = current_app.config.get('DATABASE_PATH', 'economy.db')
        else:
            self.db_path = db_path
        
        self.settings_repo = SettingsRepository(self.db_path)
        self.log_repo = AdminLogRepository(self.db_path)

    def get_all_settings(self) -> List[Dict[str, Any]]:
        """Returns all settings as a list of dictionaries."""
        settings = self.settings_repo.find_all()
        return [s.to_dict() for s in settings]

    def update_settings(self, settings_data: List[Dict[str, str]], admin_name: str) -> Dict[str, Any]:
        """
        Updates multiple settings and logs the action.
        
        Args:
            settings_data: A list of dictionaries, where each dict has 'key' and 'value'.
            admin_name: The name of the admin performing the update.

        Returns:
            A dictionary indicating the result.
        """
        updated_count = 0
        try:
            for setting in settings_data:
                key = setting.get('key')
                value = setting.get('value')
                if key and value is not None:
                    self.settings_repo.update(key, value, admin_name)
                    updated_count += 1
            
            if updated_count > 0:
                log_details = {
                    "updated_settings": [s['key'] for s in settings_data if s.get('key')],
                    "count": updated_count
                }
                self.log_repo.create(
                    admin_name=admin_name,
                    action_type='update_settings',
                    details=str(log_details)
                )

            return {'success': True, 'updated_count': updated_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}
