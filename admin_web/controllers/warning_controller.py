"""Warning controller"""
from flask import request, jsonify
from admin_web.services.warning_service import WarningService


class WarningController:
    """경고 API 컨트롤러"""

    def __init__(self):
        self.warning_service = WarningService()

    def get_warnings(self):
        """경고 목록 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))

            result = self.warning_service.get_warnings(page, limit)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def get_user_warnings(self, mastodon_id):
        """유저별 경고 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))

            result = self.warning_service.get_user_warnings(mastodon_id, page, limit)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def create_warning(self):
        """경고 생성 API"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            reason = data.get('reason')
            count = data.get('count', 1)
            admin_name = data.get('admin_name')

            if not user_id or not reason:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'user_id and reason are required'
                    }
                }), 400

            warning = self.warning_service.create_warning(user_id, reason, count, admin_name)
            return jsonify(warning.to_dict()), 201
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500
