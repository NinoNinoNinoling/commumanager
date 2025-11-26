import os
import hmac
import hashlib
import logging
from flask import Blueprint, request, jsonify
from admin_web.services.webhook_service import WebhookService

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhooks')
logger = logging.getLogger(__name__)

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """HMAC 서명 검증"""
    if not signature or not signature.startswith('sha256='):
        return False
    
    expected = signature[7:]
    computed = hmac.new(
        secret.encode('utf-8'), 
        payload, 
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, computed)

@webhook_bp.route('/mastodon', methods=['POST'])
def handle_mastodon_webhook():
    secret = os.environ.get('MASTODON_WEBHOOK_SECRET', '')
    signature = request.headers.get('X-Hub-Signature')
    payload = request.get_data()

    if not verify_signature(payload, signature, secret):
        logger.warning("웹훅 서명 검증 실패")
        return jsonify({'error': 'Invalid signature'}), 403

    try:
        data = request.get_json()
        event = data.get('event')
        logger.info(f"웹훅 수신: {event}")

        service = WebhookService()

        # 1. 계정 생성 (가입)
        if event == 'account.created':
            result = service.handle_account_created(data)
            logger.info(f"유저 가입 처리: {result.get('username')}")
            return jsonify(result), 200

        # 2. 계정 정보 변경 (역할, 프로필 수정 등)
        elif event == 'account.updated':
            # account.created와 동일한 로직을 타면 됩니다 (UPSERT 처리되어 있음)
            result = service.handle_account_created(data)
            logger.info(f"유저 정보 동기화: {result.get('username')}")
            return jsonify(result), 200

        # 그 외 이벤트 (글 작성 등) - 일단 무시
        else:
            return jsonify({'status': 'ignored'}), 200

    except Exception as e:
        logger.error(f"웹훅 처리 에러: {e}")
        return jsonify({'error': str(e)}), 500
