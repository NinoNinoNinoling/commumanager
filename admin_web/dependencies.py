"""
의존성 주입(Dependency Injection) 컨테이너

Flask의 g 객체를 사용하여 요청(Request) 수명 주기 동안 
서비스 인스턴스를 싱글톤처럼 재사용합니다.
"""
from flask import g
from admin_web.services.user_service import UserService
from admin_web.services.dashboard_service import DashboardService
from admin_web.services.warning_service import WarningService
from admin_web.services.item_service import ItemService
from admin_web.services.settings_service import SettingsService

def get_user_service() -> UserService:
    if 'user_service' not in g:
        g.user_service = UserService()
    return g.user_service

def get_dashboard_service() -> DashboardService:
    if 'dashboard_service' not in g:
        g.dashboard_service = DashboardService()
    return g.dashboard_service

def get_warning_service() -> WarningService:
    if 'warning_service' not in g:
        g.warning_service = WarningService()
    return g.warning_service

def get_item_service() -> ItemService:
    if 'item_service' not in g:
        g.item_service = ItemService()
    return g.item_service

def get_settings_service() -> SettingsService:
    if 'settings_service' not in g:
        g.settings_service = SettingsService()
    return g.settings_service
