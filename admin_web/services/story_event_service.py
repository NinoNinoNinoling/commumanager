"""StoryEventService"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from admin_web.models.story_event import StoryEvent, StoryPost
from admin_web.repositories.story_event_repository import StoryEventRepository


class StoryEventService:
    """
    스토리 이벤트 관리 비즈니스 로직을 위한 Service

    여러 포스트를 일정 간격으로 자동 발송하는 스토리 이벤트의 생성 및 포스트 추가를 처리합니다.
    """

    def __init__(self, db_path: str = 'economy.db'):
        self.story_repo = StoryEventRepository(db_path)

    def create_event(self, title: str, start_time: datetime, created_by: str, interval_minutes: int = 5) -> Dict[str, Any]:
        """
        스토리 이벤트를 생성합니다.

        Args:
            title: 이벤트 제목
            start_time: 첫 번째 포스트 발송 시각
            created_by: 이벤트 생성자 (관리자명)
            interval_minutes: 포스트 간 발송 간격 (분 단위, 기본값 5분)

        Returns:
            생성된 이벤트를 담은 딕셔너리 {'event': StoryEvent}
        """
        event = StoryEvent(title=title, start_time=start_time, created_by=created_by, interval_minutes=interval_minutes)
        created = self.story_repo.create(event)
        return {'event': created}

    def add_posts(self, event_id: int, posts_content: List[str]) -> Dict[str, Any]:
        """
        스토리 이벤트에 포스트들을 추가합니다.

        Args:
            event_id: 포스트를 추가할 스토리 이벤트 ID
            posts_content: 포스트 내용 목록 (순서대로 발송됨)

        Returns:
            생성된 포스트 목록과 개수를 담은 딕셔너리 {'posts': List[StoryPost], 'count': int}
        """
        posts = []
        for seq, content in enumerate(posts_content, start=1):
            post = StoryPost(event_id=event_id, sequence=seq, content=content)
            created_post = self.story_repo.add_post(post)
            posts.append(created_post)
        return {'posts': posts, 'count': len(posts)}
