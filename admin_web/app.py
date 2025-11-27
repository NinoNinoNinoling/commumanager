"""Flask 애플리케이션 메인"""
import os
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from admin_web.routes.web import web_bp
from admin_web.routes.api import api_bp
from admin_web.routes.webhook import webhook_bp

logger = logging.getLogger(__name__)

def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__)

    # 1. 기본 설정
    app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', 'economy.db')
    
    # 2. 보안 키 설정
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        if os.environ.get('FLASK_ENV') == 'production':
            raise RuntimeError("SECRET_KEY 환경 변수가 설정되지 않았습니다. 프로덕션을 위해 반드시 설정해주세요.")
        logger.warning("SECRET_KEY가 설정되지 않았습니다. 임시 키를 사용합니다.")
        secret_key = 'dev-secret-key-change-in-prod'
    app.secret_key = secret_key

    # 3. CSRF 보호 초기화
    csrf = CSRFProtect(app)
    csrf.exempt(webhook_bp)  # 웹훅 예외 처리

    # 4. 세션 보안 설정
    is_production = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_SECURE'] = is_production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # 5. 마스토돈 및 기타 필수 환경 변수 로드
    app.config['MASTODON_INSTANCE_URL'] = os.getenv('MASTODON_INSTANCE_URL')
    app.config['MASTODON_CLIENT_ID'] = os.getenv('MASTODON_CLIENT_ID')
    app.config['MASTODON_CLIENT_SECRET'] = os.getenv('MASTODON_CLIENT_SECRET')
    app.config['BOT_ACCESS_TOKEN'] = os.getenv('BOT_ACCESS_TOKEN')
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')

    # 6. Blueprint 등록
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(webhook_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
