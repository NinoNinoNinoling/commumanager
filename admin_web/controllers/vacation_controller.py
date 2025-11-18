"""Vacation controller"""
from flask import request, jsonify
from admin_web.services.vacation_service import VacationService


class VacationController:
    """휴가 API 컨트롤러"""

    def __init__(self):
        self.vacation_service = VacationService()

    def get_vacations(self):
        """휴가 목록 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))

            result = self.vacation_service.get_vacations(page, limit)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def create_vacation(self):
        """휴가 생성 API"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            reason = data.get('reason')
            admin_name = data.get('admin_name')

            if not user_id or not start_date or not end_date:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'user_id, start_date, and end_date are required'
                    }
                }), 400

            vacation = self.vacation_service.create_vacation(
                user_id, start_date, end_date, start_time, end_time, reason, admin_name
            )
            return jsonify(vacation.to_dict()), 201
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def delete_vacation(self, vacation_id):
        """휴가 삭제 API"""
        try:
            data = request.get_json() or {}
            admin_name = data.get('admin_name')

            success = self.vacation_service.delete_vacation(vacation_id, admin_name)
            if success:
                return jsonify({'message': 'Vacation deleted'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Vacation not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500
