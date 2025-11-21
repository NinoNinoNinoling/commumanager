"""Flask 애플리케이션 메인"""
from flask import Flask
from admin_web.routes.web import web_bp
from admin_web.routes.api import api_bp


def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__)
    app.secret_key = 'dev-secret-key-change-in-production'
    
    # Blueprint 등록
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
