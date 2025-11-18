"""
Main Routes
메인 페이지 라우트 (인덱스, 대시보드)
"""
from flask import Blueprint, render_template, redirect, url_for, session
from admin_web.controllers.dashboard_controller import DashboardController

# Blueprint 생성
main_bp = Blueprint('main', __name__)

# Controller 인스턴스 (나중에 초기화)
dashboard_controller = None


def init_main_routes(app):
    """
    메인 라우트 초기화

    Args:
        app: Flask app 인스턴스
    """
    global dashboard_controller
    dashboard_controller = DashboardController()


@main_bp.route('/')
def index():
    """인덱스 페이지"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    """대시보드 (로그인 필수)"""
    return dashboard_controller.show_dashboard()
