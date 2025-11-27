import pytest
from unittest.mock import Mock, patch, ANY
from datetime import datetime
from admin_web.services.warning_service import WarningService
from admin_web.models.user import User
from admin_web.models.warning import Warning

@pytest.fixture
def warning_service():
    with patch('admin_web.repositories.user_repository.UserRepository') as MockUserRepo,          patch('admin_web.repositories.warning_repository.WarningRepository') as MockWarningRepo,          patch('admin_web.repositories.ban_record_repository.BanRecordRepository') as MockBanRepo:
        
        mock_user_repo = MockUserRepo.return_value
        mock_warning_repo = MockWarningRepo.return_value
        mock_ban_repo = MockBanRepo.return_value
        
        service = WarningService(db_path=":memory:")
        service.user_repo = mock_user_repo
        service.warning_repo = mock_warning_repo
        
        yield service, mock_user_repo, mock_warning_repo, mock_ban_repo

def test_create_warning_wrapper(warning_service):
    """create_warning 래퍼 메서드가 issue_warning을 잘 호출하는지 검증"""
    service, mock_user_repo, mock_warning_repo, _ = warning_service
    
    # Given
    user = User(mastodon_id='u1', username='u1', display_name='User 1', role='user', warning_count=0, created_at=datetime.now())
    mock_user_repo.find_by_id.return_value = user
    mock_warning_repo.create.return_value = Warning(user_id='u1', warning_type='activity', message='test', admin_name='admin')

    # When
    data = {
        'user_id': 'u1',
        'type': 'activity',
        'message': 'Low activity',
        'admin_name': 'admin'
    }
    service.create_warning(data)

    # Then
    # [수정] connection 인자가 무엇이든 상관없도록 ANY 사용 (또는 mock_user_repo.increment_warning_count.call_args 검사)
    mock_warning_repo.create.assert_called_once()
    
    # increment_warning_count가 'u1'과 connection 객체(ANY)와 함께 호출되었는지 확인
    mock_user_repo.increment_warning_count.assert_called_with('u1', connection=ANY)

def test_auto_ban_logic(warning_service):
    """경고 3회 시 자동 밴 로직 호출 검증"""
    service, mock_user_repo, mock_warning_repo, _ = warning_service
    
    # Given
    user_after_warning = User(mastodon_id='u2', username='u2', display_name='User 2', role='user', warning_count=3, created_at=datetime.now())
    mock_user_repo.find_by_id.return_value = user_after_warning
    
    # BanRecordRepository 내부 생성 모킹
    with patch('admin_web.services.warning_service.BanRecordRepository') as MockBanRepoClass:
        mock_ban_repo_instance = MockBanRepoClass.return_value
        mock_ban_repo_instance.find_active_ban.return_value = False
        
        # When
        service.issue_warning('u2', 'activity', 'Final warning', 'admin')
        
        # Then
        mock_ban_repo_instance.create.assert_called_once()
