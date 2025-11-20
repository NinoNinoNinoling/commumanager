"""Story Event service"""
from typing import List, Optional
from datetime import datetime, timedelta
from admin_web.models.story_event import StoryEvent, StoryPost
from admin_web.repositories.story_event_repository import StoryEventRepository, StoryPostRepository
from admin_web.repositories.admin_log_repository import AdminLogRepository
from admin_web.models.admin_log import AdminLog


class StoryEventService:
    """스토리 이벤트 비즈니스 로직"""

    def __init__(self):
        self.event_repo = StoryEventRepository()
        self.post_repo = StoryPostRepository()
        self.admin_log_repo = AdminLogRepository()

    def get_events(self, page: int = 1, limit: int = 50, status: str = None) -> dict:
        """이벤트 목록 조회"""
        events, total = self.event_repo.find_all(page, limit, status)
        total_pages = (total + limit - 1) // limit

        # 각 이벤트에 포스트 개수 추가
        events_with_counts = []
        for event in events:
            event_dict = event.to_dict()
            posts = self.post_repo.find_by_event(event.id)
            event_dict['post_count'] = len(posts)
            events_with_counts.append(event_dict)

        return {
            'events': events_with_counts,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
            }
        }

    def get_event(self, event_id: int) -> Optional[StoryEvent]:
        """이벤트 조회 (포스트 포함)"""
        return self.event_repo.find_by_id(event_id, include_posts=True)

    def create_event(self, title: str, description: str = None,
                    calendar_event_id: int = None, start_time: str = None,
                    interval_minutes: int = 5, admin_name: str = None) -> StoryEvent:
        """이벤트 생성"""
        event = StoryEvent(
            id=None,
            title=title,
            description=description,
            calendar_event_id=calendar_event_id,
            start_time=datetime.fromisoformat(start_time.replace('Z', '+00:00')),
            interval_minutes=interval_minutes,
            status='pending',
            created_by=admin_name or 'admin',
        )
        created_event = self.event_repo.create(event)

        if admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='create_story_event',
                details=f"{title}",
            )
            self.admin_log_repo.create(log)

        return created_event

    def update_event(self, event_id: int, title: str, description: str = None,
                    calendar_event_id: int = None, start_time: str = None,
                    interval_minutes: int = 5, status: str = 'pending',
                    admin_name: str = None) -> bool:
        """이벤트 수정"""
        event = StoryEvent(
            id=event_id,
            title=title,
            description=description,
            calendar_event_id=calendar_event_id,
            start_time=datetime.fromisoformat(start_time.replace('Z', '+00:00')),
            interval_minutes=interval_minutes,
            status=status,
            created_by=admin_name or 'admin',
        )
        success = self.event_repo.update(event)

        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='update_story_event',
                details=f"event_id: {event_id}",
            )
            self.admin_log_repo.create(log)

        return success

    def delete_event(self, event_id: int, admin_name: str = None) -> bool:
        """이벤트 삭제 (포스트도 함께 삭제됨)"""
        success = self.event_repo.delete(event_id)

        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='delete_story_event',
                details=f"event_id: {event_id}",
            )
            self.admin_log_repo.create(log)

        return success

    def add_posts(self, event_id: int, posts_data: List[dict], admin_name: str = None) -> List[StoryPost]:
        """이벤트에 포스트 추가"""
        created_posts = []
        for idx, post_data in enumerate(posts_data):
            post = StoryPost(
                id=None,
                event_id=event_id,
                sequence=post_data.get('sequence', idx + 1),
                content=post_data['content'],
                media_urls=post_data.get('media_urls'),
                status='pending',
            )
            created = self.post_repo.create(post)
            created_posts.append(created)

        if admin_name and created_posts:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='add_story_posts',
                details=f"event_id: {event_id}, {len(created_posts)} posts added",
            )
            self.admin_log_repo.create(log)

        return created_posts

    def update_post(self, post_id: int, sequence: int, content: str,
                   media_urls: List[str] = None, status: str = 'pending',
                   admin_name: str = None) -> bool:
        """포스트 수정"""
        existing = self.post_repo.find_by_id(post_id)
        if not existing:
            return False

        post = StoryPost(
            id=post_id,
            event_id=existing.event_id,
            sequence=sequence,
            content=content,
            media_urls=media_urls,
            status=status,
        )
        success = self.post_repo.update(post)

        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='update_story_post',
                details=f"post_id: {post_id}",
            )
            self.admin_log_repo.create(log)

        return success

    def delete_post(self, post_id: int, admin_name: str = None) -> bool:
        """포스트 삭제"""
        success = self.post_repo.delete(post_id)

        if success and admin_name:
            log = AdminLog(
                id=None,
                admin_name=admin_name,
                action_type='delete_story_post',
                details=f"post_id: {post_id}",
            )
            self.admin_log_repo.create(log)

        return success

    def bulk_create_from_excel(self, excel_data: List[dict], admin_name: str = None) -> dict:
        """엑셀에서 일괄 생성"""
        created_events = []
        failed = []

        # 엑셀 형식: event_title | start_time | interval_minutes | post_content | post_media_urls
        # 같은 event_title은 하나의 이벤트로 묶임
        events_dict = {}

        for idx, row in enumerate(excel_data):
            try:
                event_title = row.get('event_title')
                if not event_title:
                    failed.append({
                        'row': idx + 1,
                        'error': 'event_title is required',
                        'data': row
                    })
                    continue

                if event_title not in events_dict:
                    events_dict[event_title] = {
                        'title': event_title,
                        'start_time': row.get('start_time'),
                        'interval_minutes': row.get('interval_minutes', 5),
                        'posts': []
                    }

                events_dict[event_title]['posts'].append({
                    'content': row.get('post_content', ''),
                    'media_urls': row.get('post_media_urls'),
                })

            except Exception as e:
                failed.append({
                    'row': idx + 1,
                    'error': str(e),
                    'data': row
                })

        # 이벤트 생성
        for event_title, event_data in events_dict.items():
            try:
                # 이벤트 생성
                event = self.create_event(
                    title=event_data['title'],
                    start_time=event_data['start_time'],
                    interval_minutes=event_data['interval_minutes'],
                    admin_name=admin_name,
                )

                # 포스트 추가
                self.add_posts(event.id, event_data['posts'], admin_name=admin_name)

                created_events.append(event.to_dict())

            except Exception as e:
                failed.append({
                    'event_title': event_title,
                    'error': str(e),
                    'data': event_data
                })

        return {
            'created': created_events,
            'failed': failed,
            'summary': {
                'total_events': len(events_dict),
                'success': len(created_events),
                'failed': len(failed),
            }
        }
