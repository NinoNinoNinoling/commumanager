import os
import hmac
import hashlib
import json
import sys
from flask import Blueprint, request, jsonify
from admin_web.services.webhook_service import WebhookService

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhooks')

# [핵심] Gunicorn이 로그를 삼키지 못하게 강제로 출력하는 함수
def force_print(msg):
    print(f"[강제출력] {msg}", file=sys.stdout, flush=True)

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not signature or not signature.startswith('sha256='):
        return False
    expected = signature[7:]
    computed = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, computed)

@webhook_bp.route('/mastodon', methods=['POST'])
def handle_mastodon_webhook():
    # 요청 오면 무조건 찍음
    force_print("🔥 HIT! 웹훅 요청 도착!")
    
    secret = os.environ.get('MASTODON_WEBHOOK_SECRET', '')
    signature = request.headers.get('X-Hub-Signature')
    payload = request.get_data()

    # 데이터 내용 날것 그대로 출력
    try:
        raw_data = payload.decode('utf-8')
        force_print(f"📦 받은 데이터: {raw_data}")
    except:
        force_print("데이터 디코딩 실패")

    if not verify_signature(payload, signature, secret):
        force_print(f"🚨 서명 실패: {signature}")
        return jsonify({'error': 'Invalid signature'}), 403

    try:
        data = request.get_json()
        event = data.get('event')
        force_print(f"👉 이벤트 타입: {event}")

        service = WebhookService()
        
        if event == 'account.created':
            force_print("✅ 가입 로직 실행 중...")
            result = service.handle_account_created(data)
            force_print("✅ 로직 완료!")
            return jsonify(result), 200
        else:
            force_print(f"⛔ 무시된 이벤트: {event}")
            return jsonify({'status': 'ignored'}), 200

    except Exception as e:
        force_print(f"❌ 에러 발생: {e}")
        return jsonify({'error': str(e)}), 500
