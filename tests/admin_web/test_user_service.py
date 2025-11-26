import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from admin_web.services.user_service import UserService
from admin_web.models.user import User

@pytest.fixture
def user_service():
    with patch('admin_web.repositories.user_repository.UserRepository') as MockUserRepository:
        mock_repo_instance = MockUserRepository.return_value
        service = UserService(db_path=":memory:")
        # [수정] 실제 UserService 내부 속성명인 user_repo로 Mock 주입
        service.user_repo = mock_repo_instance 
        yield service, mock_repo_instance

def test_get_all_users_calls_repository(user_service):
    """get_all_users 메서드가 Repository를 호출하는지 검증"""
    service, mock_repo = user_service
    
    mock_users = [
        User(mastodon_id='u1', username='user1', display_name='U1', role='user', created_at=datetime.now()),
        User(mastodon_id='u2', username='user2', display_name='U2', role='user', created_at=datetime.now())
    ]
    mock_repo.find_all_non_system_users.return_value = mock_users

    # [수정] 메서드명 get_all_users로 변경
    users = service.get_all_users()

    mock_repo.find_all_non_system_users.assert_called_once()
    assert users == mock_users
    assert len(users) == 2

def test_get_user_calls_repository(user_service):
    """get_user 메서드가 find_by_id를 호출하는지 검증"""
    service, mock_repo = user_service
    
    mock_user = User(mastodon_id='test_id', username='test', display_name='Test', role='user', created_at=datetime.now())
    mock_repo.find_by_id.return_value = mock_user

    # [수정] 메서드명 get_user로 변경
    user = service.get_user('test_id')

    mock_repo.find_by_id.assert_called_once_with('test_id')
    assert user == mock_user

def test_update_user_role_calls_repository(user_service):
    """update_user_role 메서드 검증"""
    service, mock_repo = user_service
    
    # find_by_id가 유저를 반환해야 함
    mock_repo.find_by_id.return_value = User(mastodon_id='uid', username='u', display_name='d', role='user', created_at=datetime.now())
    mock_repo.update_role.return_value = None

    service.update_user_role('uid', 'admin')

    mock_repo.update_role.assert_called_once_with('uid', 'admin')
