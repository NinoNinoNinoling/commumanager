"""Story Event controller"""
from flask import request, jsonify
from admin_web.services.story_event_service import StoryEventService
import openpyxl


class StoryEventController:
    """스토리 이벤트 API 컨트롤러"""

    def __init__(self):
        self.story_service = StoryEventService()

    def get_events(self):
        """이벤트 목록 조회 API"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            status = request.args.get('status')

            result = self.story_service.get_events(page, limit, status)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def get_event(self, event_id):
        """이벤트 상세 조회 API (포스트 포함)"""
        try:
            event = self.story_service.get_event(event_id)
            if event:
                return jsonify(event.to_dict()), 200
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

    def create_event(self):
        """이벤트 생성 API"""
        try:
            data = request.get_json()
            title = data.get('title')
            description = data.get('description')
            calendar_event_id = data.get('calendar_event_id')
            start_time = data.get('start_time')
            interval_minutes = data.get('interval_minutes', 5)
            admin_name = data.get('admin_name')

            if not title or not start_time:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'title and start_time are required'
                    }
                }), 400

            event = self.story_service.create_event(
                title, description, calendar_event_id, start_time,
                interval_minutes, admin_name
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
            calendar_event_id = data.get('calendar_event_id')
            start_time = data.get('start_time')
            interval_minutes = data.get('interval_minutes', 5)
            status = data.get('status', 'pending')
            admin_name = data.get('admin_name')

            if not title or not start_time:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'title and start_time are required'
                    }
                }), 400

            success = self.story_service.update_event(
                event_id, title, description, calendar_event_id, start_time,
                interval_minutes, status, admin_name
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

            success = self.story_service.delete_event(event_id, admin_name)
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

    def add_posts(self, event_id):
        """이벤트에 포스트 추가 API"""
        try:
            data = request.get_json()
            posts_data = data.get('posts', [])
            admin_name = data.get('admin_name')

            if not posts_data:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'posts array is required'
                    }
                }), 400

            posts = self.story_service.add_posts(event_id, posts_data, admin_name)
            return jsonify({
                'message': f'{len(posts)} posts added',
                'posts': [p.to_dict() for p in posts]
            }), 201
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def update_post(self, post_id):
        """포스트 수정 API"""
        try:
            data = request.get_json()
            sequence = data.get('sequence')
            content = data.get('content')
            media_urls = data.get('media_urls')
            status = data.get('status', 'pending')
            admin_name = data.get('admin_name')

            if not content:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'content is required'
                    }
                }), 400

            success = self.story_service.update_post(
                post_id, sequence, content, media_urls, status, admin_name
            )
            if success:
                return jsonify({'message': 'Post updated'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Post not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def delete_post(self, post_id):
        """포스트 삭제 API"""
        try:
            data = request.get_json() or {}
            admin_name = data.get('admin_name')

            success = self.story_service.delete_post(post_id, admin_name)
            if success:
                return jsonify({'message': 'Post deleted'}), 200
            else:
                return jsonify({
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Post not found'
                    }
                }), 404
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500

    def bulk_upload_excel(self):
        """엑셀 일괄 업로드 API"""
        try:
            if 'file' not in request.files:
                return jsonify({
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'No file provided'
                    }
                }), 400

            file = request.files['file']
            admin_name = request.form.get('admin_name')

            if not file.filename.endswith(('.xlsx', '.xls')):
                return jsonify({
                    'error': {
                        'code': 'INVALID_FILE_TYPE',
                        'message': 'Only Excel files (.xlsx, .xls) are supported'
                    }
                }), 400

            # 엑셀 파일 파싱
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            excel_data = []
            # 첫 행은 헤더로 간주
            # 예상 컬럼: event_title | start_time | interval_minutes | post_content | post_media_urls
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0]:  # event_title이 없으면 건너뜀
                    continue

                row_data = {
                    'event_title': str(row[0]),
                    'start_time': row[1] if isinstance(row[1], str) else row[1].isoformat() if row[1] else None,
                    'interval_minutes': int(row[2]) if row[2] else 5,
                    'post_content': str(row[3]) if len(row) > 3 and row[3] else '',
                }

                # media_urls가 있으면 쉼표로 분리
                if len(row) > 4 and row[4]:
                    media_urls = [url.strip() for url in str(row[4]).split(',')]
                    row_data['post_media_urls'] = media_urls

                excel_data.append(row_data)

            # 일괄 생성
            result = self.story_service.bulk_create_from_excel(excel_data, admin_name)
            return jsonify(result), 201

        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }), 500
