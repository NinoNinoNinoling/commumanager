"""
봇 유틸리티 모듈
"""
import os
import logging
import sys
import re
from mastodon import Mastodon

def setup_logger(name):
    """로거 설정"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger('bot.utils')

def create_mastodon_client(access_token=None):
    """
    Mastodon 클라이언트 생성
    """
    if not access_token:
        access_token = os.getenv('SYSTEM_ACCESS_TOKEN') or os.getenv('BOT_ACCESS_TOKEN')

    if not access_token:
        logger.error("❌ 봇 액세스 토큰을 찾을 수 없습니다.")
        raise ValueError("Access token is required")

    api_base_url = os.getenv('MASTODON_INSTANCE_URL')
    
    if not api_base_url:
        logger.error("❌ MASTODON_INSTANCE_URL 환경 변수가 없습니다.")
        raise ValueError("MASTODON_INSTANCE_URL must be set")

    logger.info(f"🐘 마스토돈 연결 시도: {api_base_url}")

    try:
        return Mastodon(
            access_token=access_token,
            api_base_url=api_base_url,
            ratelimit_method='wait'
        )
    except Exception as e:
        logger.error(f"❌ 마스토돈 클라이언트 생성 실패: {e}")
        raise e

def send_dm(mastodon, username, message):
    """DM 발송 헬퍼"""
    try:
        if not username.startswith('@'):
            results = mastodon.account_search(username, limit=1)
        else:
            results = mastodon.account_search(username, limit=1)
            
        if not results:
            logger.error(f"DM 발송 실패: 사용자를 찾을 수 없음 ({username})")
            return False

        user_id = results[0]['id']
        
        mastodon.status_post(
            status=message,
            visibility='direct',
            in_reply_to_id=None
        )
        return True
    except Exception as e:
        logger.error(f"DM 발송 중 오류 발생: {e}")
        return False

def favorite_status(mastodon, status_id):
    """게시글 좋아요 (반응)"""
    try:
        mastodon.status_favourite(status_id)
        return True
    except Exception as e:
        logger.error(f"좋아요 실패 (status={status_id}): {e}")
        return False

def format_currency(amount):
    """통화 포맷팅 (예: 1,000코인)"""
    return f"{amount:,}코인"

def parse_mention_command(content):
    """멘션 내용에서 명령어와 인자 파싱"""
    # HTML 태그 제거 후 텍스트만 추출 (간단한 방식)
    text = re.sub(r'<[^>]+>', '', content).strip()
    
    # @아이디 부분 제거 (맨 앞의 멘션된 계정)
    parts = text.split()
    if parts and parts[0].startswith('@'):
        parts = parts[1:]
    
    if not parts:
        return None, []
        
    command = parts[0]
    args = parts[1:]
    return command, args

def sanitize_html(content):
    """HTML 태그 제거"""
    return re.sub(r'<[^>]+>', '', content).strip()

def truncate_text(text, length=500):
    """긴 텍스트 자르기"""
    if len(text) <= length:
        return text
    return text[:length] + "..."

def invalidate_user_cache(user_id):
    """유저 캐시 무효화 (필요 시 구현)"""
    pass
