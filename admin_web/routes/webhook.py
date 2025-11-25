"""마스토돈 웹훅 라우트"""
import os
import hmac
import hashlib
import logging
from flask import Blueprint, request, jsonify

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhooks')
logger = logging.getLogger(__name__)


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    마스토돈 웹훅 HMAC 서명을 검증합니다.

    Args:
        payload: 요청 본문 (bytes)
        signature: X-Hub-Signature 헤더 값
        secret: 웹훅 비밀키

    Returns:
        서명이 유효하면 True, 아니면 False
    """
    if not signature:
        logger.warning("서명 헤더가 없습니다")
        return False

    # Mastodon은 "sha256=..." 형식으로 서명을 보냄
    if not signature.startswith('sha256='):
        logger.warning(f"잘못된 서명 형식: {signature[:20]}...")
        return False

    expected_signature = signature[7:]  # "sha256=" 제거
    computed_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, computed_signature)


@webhook_bp.route('/mastodon', methods=['POST'])
def handle_mastodon_webhook():
    """
    마스토돈 웹훅 이벤트를 처리합니다.

    지원하는 이벤트:
    - account.created: 새 계정 생성 시 DB에 유저 등록
    - status.created: 새 포스트 작성 (현재는 로깅만)
    - status.updated: 포스트 수정 (현재는 로깅만)
    """
    # 서명 검증
    secret = os.environ.get('MASTODON_WEBHOOK_SECRET', '')
    if not secret:
        logger.error("⚠️ MASTODON_WEBHOOK_SECRET 환경 변수가 설정되지 않았습니다!")
        return jsonify({'error': 'Webhook secret not configured'}), 500

    signature = request.headers.get('X-Hub-Signature')
    payload = request.get_data()

    if not verify_signature(payload, signature, secret):
        logger.warning("❌ 웹훅 서명 검증 실패")
        return jsonify({'error': 'Invalid signature'}), 403

    # JSON 파싱
    try:
        data = request.get_json()
    except Exception as e:
        logger.error(f"JSON 파싱 실패: {e}")
        return jsonify({'error': 'Invalid JSON'}), 400

    # 이벤트 타입 확인
    event = data.get('event')
    if not event:
        logger.warning("이벤트 타입이 없습니다")
        return jsonify({'error': 'Missing event type'}), 400

    logger.info(f"📩 웹훅 이벤트 수신: {event}")

    # 이벤트별 처리
    if event == 'account.created':
        return handle_account_created(data)
    elif event == 'status.created':
        return handle_status_created(data)
    elif event == 'status.updated':
        return handle_status_updated(data)
    else:
        logger.info(f"처리되지 않은 이벤트: {event}")
        return jsonify({'status': 'ignored', 'message': f'Event {event} not handled'}), 200


def handle_account_created(data: dict) -> tuple:
    """
    새 계정 생성 이벤트를 처리합니다.

    Args:
        data: 웹훅 페이로드

    Returns:
        (JSON 응답, HTTP 상태 코드)
    """
    from admin_web.services.webhook_service import WebhookService

    try:
        webhook_service = WebhookService()
        result = webhook_service.handle_account_created(data)

        logger.info(f"✅ 계정 생성 처리 완료: {result.get('user_id')}")
        return jsonify(result), 200

    except ValueError as e:
        logger.error(f"계정 생성 처리 실패: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception(f"계정 생성 처리 중 예외 발생: {e}")
        return jsonify({'error': 'Internal server error'}), 500


def handle_status_created(data: dict) -> tuple:
    """
    새 포스트 작성 이벤트를 처리합니다.

    Args:
        data: 웹훅 페이로드

    Returns:
        (JSON 응답, HTTP 상태 코드)
    """
    obj = data.get('object', {})
    username = obj.get('account', {}).get('username', 'unknown')
    content = obj.get('content', '')[:50]  # 첫 50자만

    logger.info(f"📝 새 포스트 작성: @{username} - {content}...")

    # 현재는 로깅만 수행
    return jsonify({'status': 'logged', 'event': 'status.created'}), 200


def handle_status_updated(data: dict) -> tuple:
    """
    포스트 수정 이벤트를 처리합니다.

    Args:
        data: 웹훅 페이로드

    Returns:
        (JSON 응답, HTTP 상태 코드)
    """
    obj = data.get('object', {})
    username = obj.get('account', {}).get('username', 'unknown')
    status_id = obj.get('id', 'unknown')

    logger.info(f"✏️ 포스트 수정: @{username} (ID: {status_id})")

    # 현재는 로깅만 수행
    return jsonify({'status': 'logged', 'event': 'status.updated'}), 200
