"""Admin Log controller"""
from flask import request, jsonify
from admin_web.services.admin_log_service import AdminLogService


class AdminLogController:
    """관리자 로그 API 컨트롤러"""

    def __init__(self):
        self.log_service = AdminLogService()

    def get_logs(self):
        """로그 목록 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            admin_name = request.args.get('admin_name')
            action = request.args.get('action')

            result = self.log_service.get_logs(page, limit, admin_name, action)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500
