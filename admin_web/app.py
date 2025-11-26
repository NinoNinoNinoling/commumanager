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

    # 환경 변수에서 SECRET_KEY 가져오기 (필수)
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        # 개발 환경 편의를 위해 기본값 제공하되 경고 로그 출력 (선택 사항)
        logger.warning("SECRET_KEY가 설정되지 않았습니다. 임시 키를 사용합니다.")
        secret_key = 'dev-secret-key-change-in-prod'
    app.secret_key = secret_key

    # CSRF 보호 초기화
    csrf = CSRFProtect(app)
    
    # [중요] 웹훅은 외부(Mastodon)에서 오므로 CSRF 토큰 검증 예외 처리
    csrf.exempt(webhook_bp) 

    # 세션 보안 설정
    # 주의: HTTPS가 아닌 로컬 개발 환경(http://localhost)에서는 SECURE=True 때문에 쿠키가 안 구워질 수 있습니다.
    # 개발 환경 변수(FLASK_ENV)에 따라 조건부 적용하는 것이 좋습니다.
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    app.config['SESSION_COOKIE_SECURE'] = is_production  # 프로덕션(HTTPS)에서만 True
    app.config['SESSION_COOKIE_HTTPONLY'] = True         # JavaScript 접근 방지
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'        # CSRF 방어

    # 마스토돈 및 기타 필수 환경 변수 로드
    app.config['MASTODON_INSTANCE_URL'] = os.getenv('MASTODON_INSTANCE_URL')
    app.config['MASTODON_CLIENT_ID'] = os.getenv('MASTODON_CLIENT_ID')
    app.config['MASTODON_CLIENT_SECRET'] = os.getenv('MASTODON_CLIENT_SECRET')
    app.config['BOT_ACCESS_TOKEN'] = os.getenv('BOT_ACCESS_TOKEN')
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')

    # Blueprint 등록
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(webhook_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
