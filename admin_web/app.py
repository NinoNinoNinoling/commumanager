"""
마녀봇 관리자 웹 애플리케이션
Flask + Mastodon OAuth + Bootstrap 5
Model - Repository - Service - Controller - Route 아키텍처
"""
import os
from flask import Flask, render_template
from dotenv import load_dotenv
from admin_web.config import config

# 환경 변수 로드
load_dotenv()


def create_app(config_name=None):
    """
    Flask 애플리케이션 팩토리 함수

    Args:
        config_name: 설정 이름 ('development', 'production', 'testing' 등)
                    None이면 FLASK_ENV 환경변수 사용

    Returns:
        Flask: 설정된 Flask 앱 인스턴스
    """
    # Flask 앱 생성
    app = Flask(__name__)

    # 설정 로드
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])

    # ============================================================================
    # Blueprint 등록
    # ============================================================================

    from admin_web.routes.api import api_bp
    from admin_web.routes.web import web_bp
    from admin_web.routes.auth import auth_bp

    # Auth Blueprint 등록 (인증)
    app.register_blueprint(auth_bp)

    # API Blueprint 등록 (JSON API)
    app.register_blueprint(api_bp)

    # Web Blueprint 등록 (HTML 페이지)
    app.register_blueprint(web_bp)

    # ============================================================================
    # 오류 핸들러
    # ============================================================================

    @app.errorhandler(404)
    def not_found(error):
        """404 오류 핸들러"""
        return {'error': {'code': 'NOT_FOUND', 'message': 'Not found'}}, 404

    @app.errorhandler(500)
    def internal_error(error):
        """500 오류 핸들러"""
        app.logger.error(f"서버 오류: {error}")
        return {'error': {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'}}, 500

    return app


# ============================================================================
# 애플리케이션 인스턴스 (모듈 레벨)
# ============================================================================

# 기본 앱 인스턴스 생성 (backward compatibility)
app = create_app()


# ============================================================================
# 애플리케이션 실행
# ============================================================================

if __name__ == '__main__':
    # DB 초기화 확인
    db_path = app.config['DATABASE_PATH']
    if not os.path.exists(db_path):
        print(f"⚠️  데이터베이스가 없습니다: {db_path}")
        print(f"   다음 명령어로 초기화하세요: python init_db.py {db_path}")
        exit(1)

    print("=" * 60)
    print("마녀봇 관리자 웹 서버 시작")
    print("=" * 60)
    print(f"환경: {app.config['DEBUG'] and 'development' or 'production'}")
    print(f"DB: {db_path}")
    print(f"API: /api/v1")
    print(f"아키텍처: Model-Repository-Service-Controller-Route")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
