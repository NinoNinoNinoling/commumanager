import pytest
import json
from unittest.mock import patch
from admin_web.app import create_app

@pytest.fixture
def client():
    """CSRF 비활성화된 테스트 클라이언트"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_services():
    with patch('admin_web.routes.api.get_user_service') as MockGetUser,          patch('admin_web.routes.api.get_dashboard_service') as MockGetDash,          patch('admin_web.routes.api.get_warning_service') as MockGetWarn:
        
        mock_user_service = MockGetUser.return_value
        mock_dash_service = MockGetDash.return_value
        mock_warn_service = MockGetWarn.return_value
        
        yield mock_user_service, mock_dash_service, mock_warn_service

def test_get_users_authenticated(client, mock_services):
    """인증된 유저 목록 조회 테스트"""
    mock_user_service, _, _ = mock_services
    mock_user_service.get_all_users.return_value = [] 
    
    with client.session_transaction() as sess:
        sess['user_id'] = 'admin'
        
    res = client.get('/api/v1/users')
    assert res.status_code == 200
    assert 'users' in res.json

def test_get_stats_authenticated(client, mock_services):
    """대시보드 통계 조회 테스트"""
    _, mock_dash_service, _ = mock_services
    mock_dash_service.get_dashboard_stats.return_value = {'total_users': 10}
    
    with client.session_transaction() as sess:
        sess['user_id'] = 'admin'
        
    res = client.get('/api/v1/dashboard/stats')
    assert res.status_code == 200
    assert res.json['stats']['total_users'] == 10

def test_post_warning_authenticated(client, mock_services):
    """경고 생성 API 테스트"""
    _, _, mock_warn_service = mock_services
    mock_warn_service.create_warning.return_value = {'status': 'success'}
    
    with client.session_transaction() as sess:
        sess['user_id'] = 'admin'
        
    data = {'user_id': 'u1', 'type': 'activity', 'message': 'warning'}
    res = client.post('/api/v1/warnings', json=data)
    
    assert res.status_code == 201
    mock_warn_service.create_warning.assert_called_once()

def test_adjust_balance_validation(client, mock_services):
    """잔액 조정 시 필수 필드 검증 테스트"""
    mock_user_service, _, _ = mock_services
    # Mock 반환값 설정 (JSON 직렬화 가능하도록)
    mock_user_service.adjust_balance.return_value = {
        'status': 'success',
        'new_balance': 200
    }

    with client.session_transaction() as sess:
        sess['user_id'] = 'admin'
    
    # 1. amount 누락
    res = client.post('/api/v1/users/u1/balance', json={'description': 'test'})
    assert res.status_code == 400
    assert 'Missing required fields' in res.text

    # 2. 정상 요청
    res = client.post('/api/v1/users/u1/balance', json={'amount': 100})
    assert res.status_code == 200

def test_post_warning_validation(client, mock_services):
    """경고 생성 시 필수 필드 검증 테스트"""
    _, _, mock_warn_service = mock_services
    mock_warn_service.create_warning.return_value = {'status': 'success'}

    with client.session_transaction() as sess:
        sess['user_id'] = 'admin'
        
    # 1. 필수 필드 누락
    res = client.post('/api/v1/warnings', json={'user_id': 'u1'}) # type, message 누락
    assert res.status_code == 400
    assert 'Missing fields' in res.text

    # 2. 정상 요청
    data = {'user_id': 'u1', 'type': 'activity', 'message': 'warn'}
    res = client.post('/api/v1/warnings', json=data)
    assert res.status_code == 201
