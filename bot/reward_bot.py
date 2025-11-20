#!/usr/bin/env python3
"""
리워드봇 - 재화 지급, 출석 체크, 명령어 처리

Mastodon Streaming API를 통해 멘션과 알림을 실시간으로 수신합니다.
재화 지급 및 출석 체크는 Celery task로도 실행됩니다.
"""
import os
import sys
import signal
from datetime import datetime
from mastodon import Mastodon, StreamListener
from dotenv import load_dotenv

# 로컬 모듈
from database import (
    get_economy_db,
    get_or_create_user,
    check_attendance,
    record_attendance,
    get_setting,
    is_global_vacation
)
from utils import (
    setup_logger,
    create_mastodon_client,
    send_dm
)
from command_handler import handle_command

# 환경변수 로드
load_dotenv()

# 로거 설정
logger = setup_logger('bot.reward_bot')


# ============================================================================
# Streaming Listener
# ============================================================================

class BotStreamListener(StreamListener):
    """실시간 Streaming 리스너"""

    def __init__(self, mastodon: Mastodon):
        super().__init__()
        self.mastodon = mastodon
        self.current_attendance_post_id = None  # 현재 출석 게시글 ID

    def on_notification(self, notification):
        """알림 수신"""
        try:
            notif_type = notification['type']

            if notif_type == 'mention':
                self.handle_mention(notification)

        except Exception as e:
            logger.error(f'알림 처리 오류: {e}', exc_info=True)

    def handle_mention(self, notification):
        """멘션 처리"""
        status = notification['status']
        account = status['account']
        status_id = status['id']
        in_reply_to_id = status.get('in_reply_to_id')

        user_id = str(account['id'])
        username = account['acct']

        logger.info(f'멘션 수신: @{username} (status_id={status_id})')

        # 사용자 확인/생성
        get_or_create_user(user_id, username, account.get('display_name'))

        # 출석 게시글 답글인지 확인
        if in_reply_to_id and self.is_attendance_post(in_reply_to_id):
            self.handle_attendance_reply(user_id, username, in_reply_to_id)
            return

        # 명령어 처리
        handle_command(self.mastodon, notification)

    def is_attendance_post(self, post_id: str) -> bool:
        """출석 게시글인지 확인"""
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM attendance_posts WHERE post_id = ?",
                (post_id,)
            )
            result = cursor.fetchone()
            return result['count'] > 0

    def handle_attendance_reply(self, user_id: str, username: str, attendance_post_id: str):
        """출석 답글 처리"""
        # 이미 출석했는지 확인
        if check_attendance(user_id, attendance_post_id):
            logger.info(f'중복 출석: {username}')
            return

        # 보상 지급
        reward = int(get_setting('attendance_base_reward', '50'))
        success = record_attendance(user_id, attendance_post_id, reward)

        if success:
            send_dm(self.mastodon, username,
                   f"출석 완료!\n보상: {reward}코인")
            logger.info(f'출석 완료: {username} - {reward}코인')
        else:
            logger.warning(f'출석 실패: {username}')

    def on_abort(self, err):
        """스트림 중단"""
        logger.error(f'Streaming 중단: {err}')

    def on_delete(self, status_id):
        """status 삭제"""
        pass

    def on_update(self, status):
        """status 업데이트"""
        pass


# ============================================================================
# 리워드봇 클래스
# ============================================================================

class RewardBot:
    """리워드봇 메인"""

    def __init__(self):
        self.mastodon = create_mastodon_client()
        self.listener = BotStreamListener(self.mastodon)
        self.running = False

    def start(self):
        """봇 시작"""
        logger.info('='*60)
        logger.info('리워드봇 시작')
        logger.info('='*60)

        # 종료 시그널 설정
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.running = True

        try:
            # 봇 계정 확인
            me = self.mastodon.account_verify_credentials()
            logger.info(f'봇 계정: @{me["acct"]} ({me["display_name"]})')

            # Streaming 시작
            logger.info('Streaming 시작...')
            self.mastodon.stream_user(self.listener, run_async=False, reconnect_async=True)

        except KeyboardInterrupt:
            logger.info('사용자에 의해 중단됨')
        except Exception as e:
            logger.error(f'봇 실행 실패: {e}', exc_info=True)
        finally:
            self.stop()

    def stop(self):
        """봇 종료"""
        logger.info('봇 종료 중...')
        self.running = False
        logger.info('봇 종료 완료')

    def signal_handler(self, signum, frame):
        """시그널 핸들러"""
        logger.info(f'시그널 수신: {signum}')
        self.stop()
        sys.exit(0)


# ============================================================================
# 재화 정산 (Celery task로 호출됨)
# ============================================================================

def settle_rewards():
    """
    재화 정산 (4시/16시 자동 실행)

    이전 정산 이후 답글 수를 기준으로 재화를 지급합니다.
    """
    logger.info('='*60)
    logger.info('재화 정산 시작')
    logger.info('='*60)

    mastodon = create_mastodon_client()

    # 설정 조회
    reward_reply_count = int(get_setting('reward_reply_count', '100'))  # N개당
    reward_per_replies = int(get_setting('reward_per_replies', '10'))  # M코인
    last_settlement = get_setting('last_reward_settlement_time')

    logger.info(f'보상 기준: {reward_reply_count}개당 {reward_per_replies}코인')
    logger.info(f'마지막 정산: {last_settlement}')

    # 마스토돈 DB에서 답글 카운트
    from database import get_mastodon_db, add_transaction, is_on_vacation, update_setting

    with get_mastodon_db() as pg_conn:
        pg_cursor = pg_conn.cursor()

        # 마지막 정산 이후 답글 수 집계
        if last_settlement:
            pg_cursor.execute("""
                SELECT account_id, COUNT(*) as reply_count
                FROM statuses
                WHERE in_reply_to_id IS NOT NULL
                AND created_at > %s
                GROUP BY account_id
            """, (last_settlement,))
        else:
            # 첫 정산 (최근 12시간)
            pg_cursor.execute("""
                SELECT account_id, COUNT(*) as reply_count
                FROM statuses
                WHERE in_reply_to_id IS NOT NULL
                AND created_at > NOW() - INTERVAL '12 hours'
                GROUP BY account_id
            """)

        reply_counts = pg_cursor.fetchall()

    # 재화 지급
    total_users = 0
    total_amount = 0

    for row in reply_counts:
        account_id = str(row[0])
        reply_count = row[1]

        # economy.db에 등록된 사용자인지 확인
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username FROM users WHERE mastodon_id = ?",
                (account_id,)
            )
            user = cursor.fetchone()

            if not user:
                continue  # 등록 안 된 사용자는 건너뜀

            username = user['username']

            # 휴식 중이면 정산 제외 (리워드 감소를 막기 위해)
            if is_on_vacation(account_id):
                logger.debug(f'휴식 중 - 정산 제외: {username}')
                continue

            # 재화 계산
            reward = (reply_count // reward_reply_count) * reward_per_replies

            if reward > 0:
                # 재화 지급
                add_transaction(
                    user_id=account_id,
                    transaction_type='reply',
                    amount=reward,
                    description=f'{reply_count}개 답글 작성 ({reward_reply_count}개당 {reward_per_replies}코인)'
                )

                total_users += 1
                total_amount += reward

                logger.info(f'재화 지급: {username} - {reply_count}개 답글 → {reward}코인')

    # 정산 시각 업데이트
    now = datetime.now().isoformat()
    update_setting('last_reward_settlement_time', now, 'system')

    logger.info('='*60)
    logger.info(f'재화 정산 완료: {total_users}명, 총 {total_amount:,}코인')
    logger.info('='*60)

    return {
        'total_users': total_users,
        'total_amount': total_amount,
        'timestamp': now
    }


# ============================================================================
# 출석 트윗 발행 (Celery task로 호출됨)
# ============================================================================

def post_attendance_tweet():
    """
    출석 트윗 발행 (매일 10시 자동 실행)

    리뉴얼 기간이면 발행하지 않습니다.
    """
    logger.info('='*60)
    logger.info('출석 트윗 발행 시작')
    logger.info('='*60)

    # 리뉴얼 기간 확인
    if is_global_vacation():
        logger.info('리뉴얼 기간 - 출석 트윗 발행 안 함')
        return None

    mastodon = create_mastodon_client()

    # 템플릿 조회
    template = get_setting('attendance_tweet_template',
                          '오늘도 즐거운 출석 체크!\n이 글에 답글 달면 보상이 지급됩니다!')

    # 마지막 정산 시각 안내 추가
    last_settlement = get_setting('last_reward_settlement_time')
    if last_settlement:
        settlement_time = datetime.fromisoformat(last_settlement)
        settlement_str = settlement_time.strftime('%p %I시').replace('AM', '오전').replace('PM', '오후')
        message = f"{template}\n\n※ 마지막 답글 정산 완료: {settlement_str}\n재화 지급이 완료되었습니다."
    else:
        message = template

    # 트윗 발행
    try:
        status = mastodon.status_post(message)
        post_id = status['id']

        logger.info(f'출석 트윗 발행: {post_id}')

        # DB에 기록
        from datetime import timedelta
        with get_economy_db() as conn:
            cursor = conn.cursor()
            expires_at = (datetime.now() + timedelta(hours=14)).isoformat()  # 유효기간
            cursor.execute("""
                INSERT INTO attendance_posts (post_id, expires_at)
                VALUES (?, ?)
            """, (post_id, expires_at))

        logger.info('='*60)
        logger.info('출석 트윗 발행 완료')
        logger.info('='*60)

        return {'post_id': post_id, 'content': message}

    except Exception as e:
        logger.error(f'출석 트윗 발행 실패: {e}', exc_info=True)
        return None


# ============================================================================
# 메인
# ============================================================================

if __name__ == '__main__':
    bot = RewardBot()
    bot.start()
