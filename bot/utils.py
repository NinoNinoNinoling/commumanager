"""
봇 유틸리티 함수들

Redis 캐시, Mastodon 클라이언트, 로거, 문자열 처리 등을 포함합니다.
"""
import os
import logging
import redis
from mastodon import Mastodon
from dotenv import load_dotenv
from typing import Optional

# 환경변수 로드
load_dotenv()


# ============================================================================
# 로거 설정
# ============================================================================

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    로거 설정

    Args:
        name: 로거 이름
        level: 로그 레벨

    Returns:
        logging.Logger: 설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 핸들러 생성
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # 포맷터
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # 핸들러 등록
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


# ============================================================================
# Redis 캐시
# ============================================================================

def get_redis_client() -> redis.Redis:
    """
    Redis 클라이언트 생성

    Returns:
        redis.Redis: Redis 클라이언트
    """
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        db=int(os.getenv('REDIS_DB', '0')),
        password=os.getenv('REDIS_PASSWORD', None),
        decode_responses=True
    )


def cache_user_balance(user_id: str, balance: int, ttl: int = 3600) -> None:
    """
    Redis에 사용자 잔액 캐싱 저장

    Args:
        user_id: 마스토돈 유저 ID
        balance: 잔액
        ttl: TTL (초, 기본 1시간)
    """
    try:
        r = get_redis_client()
        r.setex(f'user:balance:{user_id}', ttl, balance)
    except Exception as e:
        # Redis 오류시 무시하고 계속
        logger = setup_logger('bot.utils')
        logger.warning(f'Redis 캐싱 저장 오류: {e}')


def get_cached_user_balance(user_id: str) -> Optional[int]:
    """
    Redis에서 사용자 잔액 캐시 조회

    Args:
        user_id: 마스토돈 유저 ID

    Returns:
        Optional[int]: 캐시된 잔액 (없으면 None)
    """
    try:
        r = get_redis_client()
        balance = r.get(f'user:balance:{user_id}')
        return int(balance) if balance else None
    except Exception as e:
        logger = setup_logger('bot.utils')
        logger.warning(f'Redis 캐시 조회 오류: {e}')
        return None


def invalidate_user_cache(user_id: str) -> None:
    """
    사용자 캐시 무효화 (잔액 변경 시 호출)

    Args:
        user_id: 마스토돈 유저 ID
    """
    try:
        r = get_redis_client()
        r.delete(f'user:balance:{user_id}')
    except Exception as e:
        logger = setup_logger('bot.utils')
        logger.warning(f'Redis 캐시 삭제 오류: {e}')


# ============================================================================
# Mastodon 클라이언트
# ============================================================================

def create_mastodon_client(access_token: str = None) -> Mastodon:
    """
    Mastodon API 클라이언트 생성

    Args:
        access_token: 액세스 토큰 (기본: 환경변수 값 사용)

    Returns:
        Mastodon: Mastodon 클라이언트

    Raises:
        ValueError: 필수 환경 변수가 설정되지 않은 경우
    """
    logger = setup_logger('bot.utils')

    if access_token is None:
        access_token = os.getenv('BOT_ACCESS_TOKEN')

    # API Base URL 확인 (INTERNAL 우선, 없으면 MASTODON_INSTANCE_URL)
    api_base_url = os.getenv('INTERNAL_MASTODON_INSTANCE_URL', os.getenv('MASTODON_INSTANCE_URL'))

    # 필수 환경 변수 검증
    if not api_base_url:
        error_msg = (
            "MASTODON_INSTANCE_URL 또는 INTERNAL_MASTODON_INSTANCE_URL 환경 변수가 설정되지 않았습니다.\n"
            ".env 파일에 다음 중 하나를 설정하세요:\n"
            "  MASTODON_INSTANCE_URL=https://your-mastodon-instance.com\n"
            "  또는\n"
            "  INTERNAL_MASTODON_INSTANCE_URL=http://mastodon-web:3000"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not access_token:
        error_msg = (
            "BOT_ACCESS_TOKEN 환경 변수가 설정되지 않았습니다.\n"
            ".env 파일에 BOT_ACCESS_TOKEN을 설정하세요."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(f'Mastodon 클라이언트 생성 - URL: {api_base_url}, Token: {"설정됨" if access_token else "없음"}')

    return Mastodon(
        access_token=access_token,
        api_base_url=api_base_url
    )


def send_dm(mastodon: Mastodon, user_id: str, message: str) -> dict:
    """
    DM 발송

    Args:
        mastodon: Mastodon 클라이언트
        user_id: 수신 마스토돈 ID
        message: 메시지 내용

    Returns:
        dict: 생성된 status 객체

    Raises:
        Exception: DM 발송 오류 시
    """
    return mastodon.status_post(
        status=f'@{user_id} {message}',
        visibility='direct'
    )


def favorite_status(mastodon: Mastodon, status_id: str) -> dict:
    """
    status에 좋아요(별표) 추가

    주로 구매 성공 시 사용됩니다.

    Args:
        mastodon: Mastodon 클라이언트
        status_id: status ID

    Returns:
        dict: status 객체
    """
    return mastodon.status_favourite(status_id)


# ============================================================================
# 문자열 처리 함수
# ============================================================================

def parse_mention_command(content: str) -> tuple[str, list[str]]:
    """
    멘션 명령어 파싱

    Args:
        content: 멘션 내용 (HTML 태그 제거됨)

    Returns:
        tuple: (명령어, 나머지 인자들)

    Examples:
        "멘션 내재화" -> ("내재화", [])
        "멘션 휴식 7" -> ("휴식", ["7"])
        "멘션 구매 아이템1" -> ("구매", ["아이템1"])
    """
    # HTML 태그 제거 (Mastodon.py 파싱에서 이미 제거된 경우도 있음)
    import re
    content = re.sub(r'<[^>]+>', '', content).strip()

    # "@" 제거
    content = re.sub(r'@\S+', '', content, count=1).strip()

    # 공백으로 분할
    parts = content.split()

    if not parts:
        return '', []

    command = parts[0]
    args = parts[1:]

    return command, args


def format_currency(amount: int) -> str:
    """
    재화 금액 포맷팅

    Args:
        amount: 금액

    Returns:
        str: 포맷된 문자열

    Examples:
        1000 -> "1,000코인"
        50 -> "50코인"
    """
    return f'{amount:,}코인'


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    메시지 문자 수 제한 (마스토돈 문자 제한 대응)

    Args:
        text: 원본 메시지
        max_length: 최대 문자 수

    Returns:
        str: 잘린 메시지
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def sanitize_html(text: str) -> str:
    """
    HTML 태그 제거

    Args:
        text: HTML이 포함된 메시지

    Returns:
        str: 태그가 제거된 메시지
    """
    import re
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # HTML 엔티티 디코딩
    import html
    return html.unescape(text).strip()


def get_bot_mention_pattern() -> str:
    """
    봇 멘션 패턴 반환

    Returns:
        str: 봇 계정 (settings에서 읽음)
    """
    from .database import get_setting
    return get_setting('system_bot_account', '@봇')
