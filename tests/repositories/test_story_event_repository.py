"""
StoryEventRepository tests
"""
import sqlite3
import pytest
from datetime import datetime
from admin_web.models.story_event import StoryEvent, StoryPost
from admin_web.repositories.story_event_repository import StoryEventRepository
from init_db import initialize_database # Assuming init_db is available to set up tables

@pytest.fixture
def story_event_repo(temp_db):
    """Fixture to create a StoryEventRepository with an initialized temporary database."""
    initialize_database(temp_db) # Ensure tables are created
    return StoryEventRepository(temp_db)

@pytest.fixture
def db_connection_for_repo_test(temp_db):
    """Provides a fresh DB connection for direct DB assertions."""
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

def test_should_create_story_event(story_event_repo, db_connection_for_repo_test):
    """
    StoryEventRepository의 create() 메서드는 새 스토리 이벤트를 생성해야 한다.
    """
    # Given
    start_time = datetime(2025, 12, 25, 10, 0, 0)
    event_data = StoryEvent(
        title="크리스마스 특별 스토리",
        description="모두를 위한 따뜻한 크리스마스 스토리",
        start_time=start_time,
        interval_minutes=10,
        status="pending",
        created_by="test_admin"
    )

    # When
    created_event = story_event_repo.create(event_data)

    # Then
    assert created_event.id is not None
    assert created_event.title == "크리스마스 특별 스토리"
    assert created_event.start_time == start_time
    assert created_event.created_by == "test_admin"

    # Verify directly from DB
    cursor = db_connection_for_repo_test.cursor()
    cursor.execute("SELECT * FROM story_events WHERE id = ?", (created_event.id,))
    row = cursor.fetchone()
    assert row is not None
    assert row['title'] == "크리스마스 특별 스토리"
    assert datetime.fromisoformat(row['start_time']) == start_time
    assert row['created_by'] == "test_admin"

def test_should_find_story_event_by_id(story_event_repo, db_connection_for_repo_test):
    """
    StoryEventRepository의 find_by_id() 메서드는 ID로 스토리 이벤트를 조회해야 한다.
    """
    # Given: 이벤트 생성
    start_time = datetime(2025, 1, 1, 0, 0, 0)
    event_data = StoryEvent(
        title="새해 이벤트",
        start_time=start_time,
        created_by="test_admin"
    )
    created_event = story_event_repo.create(event_data)

    # When: ID로 조회
    found_event = story_event_repo.find_by_id(created_event.id)

    # Then
    assert found_event is not None
    assert found_event.id == created_event.id
    assert found_event.title == "새해 이벤트"
    assert found_event.start_time == start_time

def test_should_return_none_when_story_event_not_found(story_event_repo):
    """
    존재하지 않는 ID로 조회 시 None을 반환해야 한다.
    """
    # When: 존재하지 않는 ID로 조회
    found_event = story_event_repo.find_by_id(999)

    # Then
    assert found_event is None

def test_should_add_post_to_story_event(story_event_repo, db_connection_for_repo_test):
    """
    StoryEventRepository의 add_post() 메서드는 스토리 이벤트에 포스트를 추가해야 한다.
    """
    # Given: 이벤트 생성
    event_data = StoryEvent(title="테스트 이벤트", start_time=datetime.now(), created_by="test_admin")
    created_event = story_event_repo.create(event_data)

    # When: 포스트 추가
    post_data = StoryPost(event_id=created_event.id, sequence=1, content="첫 번째 포스트 내용")
    created_post = story_event_repo.add_post(post_data)

    # Then
    assert created_post.id is not None
    assert created_post.event_id == created_event.id
    assert created_post.sequence == 1
    assert created_post.content == "첫 번째 포스트 내용"

    # Verify directly from DB
    cursor = db_connection_for_repo_test.cursor()
    cursor.execute("SELECT * FROM story_posts WHERE id = ?", (created_post.id,))
    row = cursor.fetchone()
    assert row is not None
    assert row['event_id'] == created_event.id
    assert row['content'] == "첫 번째 포스트 내용"

def test_should_find_posts_by_event(story_event_repo, db_connection_for_repo_test):
    """
    StoryEventRepository의 find_posts_by_event() 메서드는 특정 이벤트의 모든 포스트를 조회해야 한다.
    """
    # Given: 이벤트 및 여러 포스트 생성
    event_data = StoryEvent(title="멀티 포스트 이벤트", start_time=datetime.now(), created_by="test_admin")
    created_event = story_event_repo.create(event_data)

    for i in range(3):
        post_data = StoryPost(event_id=created_event.id, sequence=i+1, content=f"포스트 {i+1}")
        story_event_repo.add_post(post_data)

    # When: 이벤트 ID로 포스트 조회
    posts = story_event_repo.find_posts_by_event(created_event.id)

    # Then
    assert len(posts) == 3
    assert posts[0].sequence == 1
    assert posts[1].sequence == 2
    assert posts[2].sequence == 3
    assert all(p.event_id == created_event.id for p in posts)

def test_should_return_empty_list_for_event_with_no_posts(story_event_repo):
    """
    포스트가 없는 이벤트의 포스트 조회 시 빈 리스트를 반환해야 한다.
    """
    # Given: 이벤트만 생성
    event_data = StoryEvent(title="빈 이벤트", start_time=datetime.now(), created_by="test_admin")
    created_event = story_event_repo.create(event_data)

    # When: 포스트 조회
    posts = story_event_repo.find_posts_by_event(created_event.id)

    # Then
    assert len(posts) == 0



