"""Flask 애플리케이션 메인"""
import os
import logging
from flask import Flask
from admin_web.routes.web import web_bp
from admin_web.routes.api import api_bp
from admin_web.routes.webhook import webhook_bp

logger = logging.getLogger(__name__)


def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__)

    # 환경 변수에서 SECRET_KEY 가져오기 (없으면 경고와 함께 기본값 사용)
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        logger.warning(
            "⚠️  SECRET_KEY 환경 변수가 설정되지 않았습니다! "
            "기본값 'dev-secret-key-change-in-production'을 사용 중입니다. "
            "프로덕션 환경에서는 반드시 강력한 SECRET_KEY로 변경하세요!"
        )
        secret_key = 'dev-secret-key-change-in-production'
    app.secret_key = secret_key
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
    app.run(debug=True, host='0.0.0.0', port=5000)
