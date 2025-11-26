import pytest
import json
from unittest.mock import patch
from admin_web.app import create_app

@pytest.fixture
def client():
    """CSRF 비활성화된 테스트 클라이언트"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # [중요] API 테스트를 위해 CSRF 비활성화
    
    with app.test_client() as client:
        yield client

def test_get_users_authenticated(client):
    """인증된 유저 목록 조회 테스트"""
    # Mock Service
    with patch('admin_web.routes.api.UserService') as MockUserService:
        mock_service = MockUserService.return_value
        mock_service.get_all_users.return_value = [] # 빈 리스트 반환 가정
        
        # 세션 설정 (로그인)
        with client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            
        res = client.get('/api/v1/users')
        assert res.status_code == 200
        assert 'users' in res.json

def test_get_stats_authenticated(client):
    """대시보드 통계 조회 테스트"""
    with patch('admin_web.routes.api.DashboardService') as MockDashService:
        mock_service = MockDashService.return_value
        mock_service.get_dashboard_stats.return_value = {'total_users': 10}
        
        with client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            
        res = client.get('/api/v1/dashboard/stats')
        assert res.status_code == 200
        assert res.json['stats']['total_users'] == 10

def test_post_warning_authenticated(client):
    """경고 생성 API 테스트"""
    with patch('admin_web.routes.api.WarningService') as MockWarningService:
        mock_service = MockWarningService.return_value
        mock_service.create_warning.return_value = {'status': 'success'}
        
        with client.session_transaction() as sess:
            sess['user_id'] = 'admin'
            
        data = {'user_id': 'u1', 'type': 'activity', 'message': 'warning'}
        res = client.post('/api/v1/warnings', json=data)
        
        assert res.status_code == 201
        mock_service.create_warning.assert_called_once()
