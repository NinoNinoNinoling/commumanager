#!/usr/bin/env python3
"""
Mastodon 유저 동기화 스크립트
마스토돈 서버의 유저 목록을 가져와서 economy.db와 동기화합니다.
"""
import os
import sqlite3
import logging
from mastodon import Mastodon
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수 로드 (상위 폴더의 .env 파일을 찾기 위해 경로 조정이 필요할 수 있음)
# 컨테이너 내부에서는 /app/.env 에 위치함
load_dotenv()

def get_db_connection():
    """DB 연결 (컨테이너 내부 경로 기준)"""
    db_path = '/app/economy.db'
    return sqlite3.connect(db_path)

def sync_users():
    """유저 동기화 메인 로직"""
    
    # 1. 마스토돈 API 연결
    base_url = os.getenv('MASTODON_INSTANCE_URL')
    access_token = os.getenv('BOT_ACCESS_TOKEN')
    
    if not base_url or not access_token:
        logger.error("❌ 환경변수 설정이 누락되었습니다 (URL 또는 Token).")
        return

    try:
        m = Mastodon(api_base_url=base_url, access_token=access_token)
        logger.info(f"🐘 마스토돈 서버 연결 성공: {base_url}")
        
        # 2. 로컬 유저 전체 조회 (limit=None으로 전체 조회)
        # admin_accounts_v2는 관리자 권한 필요. 일반 봇 토큰으로는 directory API 사용 가능
        # 여기서는 확실한 관리를 위해 directory API를 사용하여 로컬 유저만 긁어옵니다.
        mastodon_users = m.directory(local=True, limit=100, order='new')
        
        logger.info(f"🔍 마스토돈에서 {len(mastodon_users)}명의 유저를 발견했습니다.")

    except Exception as e:
        logger.error(f"❌ 마스토돈 API 연결 실패: {e}")
        return

    # 3. DB 동기화
    conn = get_db_connection()
    cursor = conn.cursor()
    
    added_count = 0
    updated_count = 0

    for user in mastodon_users:
        m_id = str(user['id'])
        username = user['username']
        display_name = user['display_name'] or username
        
        # 봇 계정인지 확인 (username에 'bot'이 들어가면 봇으로 간주하는 간단한 로직 추가 가능)
        role = 'bot' if '_bot' in username else 'user'
        
        # 이미 존재하는지 확인
        cursor.execute("SELECT mastodon_id FROM users WHERE mastodon_id = ?", (m_id,))
        exists = cursor.fetchone()
        
        if exists:
            # 업데이트 (이름이 바뀌었을 수 있으므로)
            cursor.execute("""
                UPDATE users 
                SET username = ?, display_name = ? 
                WHERE mastodon_id = ?
            """, (username, display_name, m_id))
            updated_count += 1
        else:
            # 신규 추가 (기본금 1000 지급)
            cursor.execute("""
                INSERT INTO users (mastodon_id, username, display_name, role, balance, total_earned)
                VALUES (?, ?, ?, ?, 1000, 1000)
            """, (m_id, username, display_name, role))
            added_count += 1
            logger.info(f"🆕 신규 유저 등록: @{username} ({role})")

    conn.commit()
    conn.close()
    
    logger.info("=" * 40)
    logger.info(f"✅ 동기화 완료!")
    logger.info(f"   - 신규 추가: {added_count}명")
    logger.info(f"   - 정보 갱신: {updated_count}명")
    logger.info("=" * 40)

if __name__ == '__main__':
    sync_users()
