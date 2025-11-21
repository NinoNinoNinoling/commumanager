"""Phase 7 Controller 테스트"""
def test_controllers_import():
    """Controller 클래스들이 제대로 import 되는지 테스트"""
    from admin_web.controllers.user_controller import UserController
    from admin_web.controllers.item_controller import ItemController
    from admin_web.controllers.dashboard_controller import DashboardController
    
    # 인스턴스 생성 테스트
    user_ctrl = UserController()
    item_ctrl = ItemController()
    dashboard_ctrl = DashboardController()
    
    assert user_ctrl is not None
    assert item_ctrl is not None
    assert dashboard_ctrl is not None
    
    print("✅ Phase 7 Controller 통합 테스트 성공!")
