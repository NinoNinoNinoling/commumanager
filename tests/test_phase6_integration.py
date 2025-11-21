"""Phase 6 통합 테스트"""
import pytest


@pytest.fixture
def admin_log_repo(temp_db):
    from init_db import initialize_database
    from admin_web.repositories.admin_log_repository import AdminLogRepository
    initialize_database(temp_db)
    return AdminLogRepository(temp_db)


def test_admin_log_integration(admin_log_repo):
    # Create log
    admin_log_repo.create_log(
        admin_name='admin',
        action_type='user_balance_update',
        target_user='user@example.com',
        details='{"amount": 100}'
    )
    
    # Find all logs
    logs = admin_log_repo.find_all(limit=10)
    assert len(logs) == 1
    assert logs[0].admin_name == 'admin'
    print("✅ Phase 6 통합 테스트 성공!")
