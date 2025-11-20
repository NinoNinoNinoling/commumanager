"""Scheduled Announcement controller"""
from flask import request, jsonify
from admin_web.services.scheduled_announcement_service import ScheduledAnnouncementService


class ScheduledAnnouncementController:
    """공지 예약 API 컨트롤러"""

    def __init__(self):
        self.announcement_service = ScheduledAnnouncementService()

    def get_announcements(self):
        """공지 목록 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            status = request.args.get('status')
            post_type = request.args.get('type')

            result = self.announcement_service.get_announcements(page, limit, status, post_type)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def get_announcement(self, announcement_id):
        """공지 상세 조회 API"""
        try:
            announcement = self.announcement_service.get_announcement(announcement_id)
            if announcement:
                return jsonify(announcement.to_dict()), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Announcement not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def create_announcement(self):
        """공지 생성 API"""
        try:
            data = request.get_json()
            post_type = data.get('post_type', 'announcement')
            content = data.get('content')
            scheduled_at = data.get('scheduled_at')
            visibility = data.get('visibility', 'public')
            is_public = data.get('is_public', True)
            admin_name = data.get('admin_name')

            if not content or not scheduled_at:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'content and scheduled_at are required'
                    }
                }), 400

            announcement = self.announcement_service.create_announcement(
                post_type, content, scheduled_at, visibility, is_public, admin_name
            )
            return jsonify(announcement.to_dict()), 201
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def update_announcement(self, announcement_id):
        """공지 수정 API"""
        try:
            data = request.get_json()
            post_type = data.get('post_type', 'announcement')
            content = data.get('content')
            scheduled_at = data.get('scheduled_at')
            visibility = data.get('visibility', 'public')
            is_public = data.get('is_public', True)
            status = data.get('status', 'pending')
            admin_name = data.get('admin_name')

            if not content or not scheduled_at:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'content and scheduled_at are required'
                    }
                }), 400

            success = self.announcement_service.update_announcement(
                announcement_id, post_type, content, scheduled_at, visibility,
                is_public, status, admin_name
            )
            if success:
                return jsonify({'message': 'Announcement updated'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Announcement not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def delete_announcement(self, announcement_id):
        """공지 삭제 API"""
        try:
            data = request.get_json() or {}
            admin_name = data.get('admin_name')

            success = self.announcement_service.delete_announcement(announcement_id, admin_name)
            if success:
                return jsonify({'message': 'Announcement deleted'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Announcement not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500
