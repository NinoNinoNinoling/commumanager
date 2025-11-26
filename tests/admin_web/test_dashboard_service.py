import pytest
from unittest.mock import Mock, patch
from admin_web.services.dashboard_service import DashboardService

@pytest.fixture
def dashboard_service():
    with patch('admin_web.repositories.dashboard_repository.DashboardRepository') as MockRepo:
        mock_repo_instance = MockRepo.return_value
        service = DashboardService(db_path=":memory:")
        # [수정] 속성명 dashboard_repo 확인 및 주입
        service.dashboard_repo = mock_repo_instance
        yield service, mock_repo_instance

def test_get_dashboard_stats_calls_repository(dashboard_service):
    """get_dashboard_stats 메서드 검증"""
    service, mock_repo = dashboard_service
    
    # Mock 반환값 설정
    mock_repo.get_total_users.return_value = 100
    mock_repo.get_active_users_24h.return_value = 50
    mock_repo.get_total_balance.return_value = 5000
    mock_repo.get_user_stats_risk_count.return_value = 5
    mock_repo.get_total_risk_users_count.return_value = 10
    mock_repo.get_on_vacation_count.return_value = 2
    mock_repo.get_scheduled_stories_count.return_value = 3
    mock_repo.get_scheduled_announcements_count.return_value = 1
    mock_repo.get_warnings_7d_count.return_value = 4

    # [수정] 메서드명 get_dashboard_stats로 변경
    stats = service.get_dashboard_stats()

    # 검증
    assert stats['total_users'] == 100
    assert stats['active_users_24h'] == 50
    assert stats['total_balance'] == 5000
    mock_repo.get_total_users.assert_called_once()
