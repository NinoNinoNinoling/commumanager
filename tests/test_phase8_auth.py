"""Phase 8 인증 테스트"""
from admin_web.utils.auth import check_permission


def test_check_permission():
    # Admin can do everything
    assert check_permission('admin', 'admin') is True
    assert check_permission('admin', 'moderator') is True
    assert check_permission('admin', 'user') is True
    
    # Moderator can't access admin
    assert check_permission('moderator', 'admin') is False
    assert check_permission('moderator', 'moderator') is True
    assert check_permission('moderator', 'user') is True
    
    # User can only access user
    assert check_permission('user', 'admin') is False
    assert check_permission('user', 'moderator') is False
    assert check_permission('user', 'user') is True
    
    print("✅ Phase 8 인증 테스트 성공!")
