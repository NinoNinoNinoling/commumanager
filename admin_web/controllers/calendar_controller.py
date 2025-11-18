"""Calendar controller"""
from flask import request, jsonify
from admin_web.services.calendar_service import CalendarService


class CalendarController:
    """캘린더 API 컨트롤러"""

    def __init__(self):
        self.calendar_service = CalendarService()

    def get_events(self):
        """이벤트 목록 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            event_type = request.args.get('type')

            result = self.calendar_service.get_events(page, limit, event_type)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def create_event(self):
        """이벤트 생성 API"""
        try:
            data = request.get_json()
            title = data.get('title')
            description = data.get('description')
            event_type = data.get('event_type', 'general')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            admin_name = data.get('admin_name')

            if not title:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'title is required'
                    }
                }), 400

            event = self.calendar_service.create_event(
                title, description, event_type, start_date, end_date,
                start_time, end_time, admin_name
            )
            return jsonify(event.to_dict()), 201
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def update_event(self, event_id):
        """이벤트 수정 API"""
        try:
            data = request.get_json()
            title = data.get('title')
            description = data.get('description')
            event_type = data.get('event_type', 'general')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            admin_name = data.get('admin_name')

            if not title:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'title is required'
                    }
                }), 400

            success = self.calendar_service.update_event(
                event_id, title, description, event_type, start_date, end_date,
                start_time, end_time, admin_name
            )
            if success:
                return jsonify({'message': 'Event updated'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Event not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def delete_event(self, event_id):
        """이벤트 삭제 API"""
        try:
            data = request.get_json() or {}
            admin_name = data.get('admin_name')

            success = self.calendar_service.delete_event(event_id, admin_name)
            if success:
                return jsonify({'message': 'Event deleted'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Event not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500
