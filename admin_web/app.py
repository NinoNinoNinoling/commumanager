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

# Flask 앱 생성
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])


# ============================================================================
# Blueprint 등록
# ============================================================================

from admin_web.routes.auth import auth_bp, init_auth_routes
from admin_web.routes.main import main_bp, init_main_routes

# Blueprint 초기화
init_auth_routes(app)
init_main_routes(app)

# Blueprint 등록
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)


# ============================================================================
# 오류 핸들러
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 오류 핸들러"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 오류 핸들러"""
    app.logger.error(f"서버 오류: {error}")
    return render_template('errors/500.html'), 500


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
    print(f"마스토돈: {app.config['MASTODON_INSTANCE_URL']}")
    print(f"아키텍처: Model-Repository-Service-Controller-Route")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
