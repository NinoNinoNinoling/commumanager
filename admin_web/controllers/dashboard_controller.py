"""DashboardController"""
from flask import jsonify
from admin_web.services.user_service import UserService
from admin_web.services.item_service import ItemService
from admin_web.utils.auth import admin_required


class DashboardController:
    def __init__(self, db_path: str = 'economy.db'):
        self.user_service = UserService(db_path)
        self.item_service = ItemService(db_path)

    @admin_required
    def get_dashboard_stats(self):
        """GET /api/v1/dashboard/stats - 대시보드 통계"""
        # 간단한 통계
        users = self.user_service.get_all_users()
        items = self.item_service.get_active_items()
        
        stats = {
            'total_users': len(users),
            'total_items': len(items),
            'total_balance': sum(u.balance for u in users),
        }
        return jsonify({'stats': stats})
