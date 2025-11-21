"""Flask 애플리케이션 메인"""
import os
from flask import Flask
from admin_web.routes.web import web_bp
from admin_web.routes.api import api_bp


def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__)

    # 환경 변수에서 SECRET_KEY 가져오기 (없으면 경고와 함께 기본값 사용)
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        print("경고: SECRET_KEY 환경 변수가 설정되지 않았습니다. 개발 모드에서만 사용하세요!")
        secret_key = 'dev-secret-key-change-in-production'
    app.secret_key = secret_key

    # Blueprint 등록
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
