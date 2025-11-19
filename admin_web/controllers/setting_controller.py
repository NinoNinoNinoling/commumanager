"""Setting controller"""
from flask import request, jsonify
from admin_web.services.setting_service import SettingService


class SettingController:
    """설정 API 컨트롤러"""

    def __init__(self):
        self.setting_service = SettingService()

    def get_settings(self):
        """전체 설정 조회 API"""
        try:
            settings = self.setting_service.get_settings()
            return jsonify({'settings': settings}), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def update_setting(self, key):
        """설정 업데이트 API"""
        try:
            data = request.get_json()
            value = data.get('value')
            admin_name = data.get('admin_name')

            if value is None:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'value is required'
                    }
                }), 400

            success = self.setting_service.update_setting(key, value, admin_name)
            if success:
                return jsonify({'message': 'Setting updated'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Setting not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500
