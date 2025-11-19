"""
Dashboard Controller
대시보드 관련 비즈니스 로직
"""
from flask import render_template, redirect, url_for, session
from admin_web.services.user_service import UserService


class DashboardController:
    """대시보드 컨트롤러"""

    def __init__(self):
        """
        Args:
            config: Flask app config
        """        self.user_service = UserService()

    def show_dashboard(self):
        """
        대시보드 표시 (로그인 필수)

        Returns:
            렌더링된 템플릿 또는 redirect
        """
        # 로그인 확인
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        # 관리자 권한 확인
        if not session.get('is_admin', False):
            return "관리자 권한이 필요합니다.", 403

        # 기본 통계 조회
        stats = self.user_service.get_user_statistics()

        return render_template('dashboard.html', stats=stats)
