"""
활동량 체크 및 분석 모듈

PostgreSQL (Mastodon DB)에서 사용자 활동량을 조회하고 분석합니다.
분석 결과를 economy DB에 기록하고 경고를 발송합니다.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from mastodon import Mastodon
from .database import (
    get_economy_db,
    get_mastodon_db,
    get_setting,
    is_on_vacation
)
from .utils import setup_logger, send_dm

logger = setup_logger('bot.activity_checker')


# ============================================================================
# 활동량 체크
# ============================================================================

def check_user_activity(user_id: str, period_hours: int = 48) -> int:
    """
    특정 기간 답글 수 조회 (PostgreSQL)

    Args:
        user_id: 마스토돈 유저 ID
        period_hours: 조회 기간 (시간)

    Returns:
        int: 답글 수
    """
    try:
        with get_mastodon_db() as conn:
            cursor = conn.cursor()

            # 최근 N시간 동안 작성한 답글 수 조회
            cursor.execute("""
                SELECT COUNT(*) as reply_count
                FROM statuses
                WHERE account_id = %s
                AND in_reply_to_id IS NOT NULL
                AND created_at > NOW() - INTERVAL '%s hours'
            """, (user_id, period_hours))

            result = cursor.fetchone()
            return result[0] if result else 0

    except Exception as e:
        logger.error(f'활동량 조회 오류 (user_id={user_id}): {e}')
        return 0


def check_all_users_activity() -> List[Dict]:
    """
    전체 사용자 활동량 체크 (4시/16시 자동 실행)

    휴식 상태인 유저는 제외하고, 기준 미달인 유저를 추출합니다.
    분석 결과를 economy DB에 기록하고 경고를 발송합니다.

    Returns:
        List[Dict]: 기준 미달 사용자 목록
    """
    logger.info('전체 사용자 활동량 체크 시작')

    period_hours = int(get_setting('check_period_hours', '48'))
    min_replies = int(get_setting('min_replies_48h', '20'))

    insufficient_users = []

    with get_economy_db() as conn:
        cursor = conn.cursor()

        # 일반 멤버 사용자 조회
        cursor.execute("""
            SELECT mastodon_id, username
            FROM users
            WHERE role = 'user'
        """)
        users = cursor.fetchall()

        for user in users:
            user_id = user['mastodon_id']
            username = user['username']

            # 휴식 중이면 건너뜀
            if is_on_vacation(user_id):
                logger.debug(f'휴식 중 - 건너뜀: {username}')
                continue

            # 활동량 조회
            reply_count = check_user_activity(user_id, period_hours)

            # 기준 미달
            if reply_count < min_replies:
                insufficient_users.append({
                    'user_id': user_id,
                    'username': username,
                    'required_replies': min_replies,
                    'actual_replies': reply_count,
                    'period_hours': period_hours
                })

                # DB에 기록 (관리자 웹에서 확인 가능)
                cursor.execute("""
                    INSERT INTO warnings
                    (user_id, warning_type, check_period_hours, required_replies, actual_replies, message, dm_sent)
                    VALUES (?, 'auto', ?, ?, ?, ?, 0)
                """, (
                    user_id,
                    period_hours,
                    min_replies,
                    reply_count,
                    f'활동량 부족 ({period_hours}시간 동안 {reply_count}개 답글, 기준: {min_replies})'
                ))

                logger.warning(f'활동량 부족: {username} - {reply_count}/{min_replies}')

    logger.info(f'활동량 체크 완료: {len(insufficient_users)}명 부족')
    return insufficient_users


# ============================================================================
# 사회성 분석
# ============================================================================

def analyze_conversation_partners(user_id: str, period_hours: int = 48) -> Dict:
    """
    대화 상대 분포 분석 (고립도, 편향도)

    Args:
        user_id: 마스토돈 유저 ID
        period_hours: 조회 기간 (시간)

    Returns:
        Dict: 분석 결과
    """
    try:
        with get_mastodon_db() as conn:
            cursor = conn.cursor()

            # 최근 N시간 대화 상대 분포
            cursor.execute("""
                SELECT
                    in_reply_to_account_id,
                    COUNT(*) as reply_count
                FROM statuses
                WHERE account_id = %s
                AND in_reply_to_id IS NOT NULL
                AND created_at > NOW() - INTERVAL '%s hours'
                GROUP BY in_reply_to_account_id
                ORDER BY reply_count DESC
            """, (user_id, period_hours))

            partners = cursor.fetchall()

            if not partners:
                return {
                    'unique_partners': 0,
                    'total_replies': 0,
                    'top_partner_id': None,
                    'top_partner_count': 0,
                    'top_partner_ratio': 0.0,
                    'is_isolated': True,
                    'is_biased': False
                }

            total_replies = sum(p[1] for p in partners)
            unique_partners = len(partners)
            top_partner_id = partners[0][0]
            top_partner_count = partners[0][1]
            top_partner_ratio = top_partner_count / total_replies if total_replies > 0 else 0.0

            # 기준값 조회
            isolation_threshold = int(get_setting('isolation_threshold', '7'))
            bias_threshold = float(get_setting('bias_threshold', '0.3'))

            return {
                'unique_partners': unique_partners,
                'total_replies': total_replies,
                'top_partner_id': str(top_partner_id),
                'top_partner_count': top_partner_count,
                'top_partner_ratio': top_partner_ratio,
                'is_isolated': unique_partners < isolation_threshold,
                'is_biased': top_partner_ratio > bias_threshold
            }

    except Exception as e:
        logger.error(f'대화 상대 분석 오류 (user_id={user_id}): {e}')
        return {
            'unique_partners': 0,
            'total_replies': 0,
            'top_partner_id': None,
            'top_partner_count': 0,
            'top_partner_ratio': 0.0,
            'is_isolated': False,
            'is_biased': False
        }


def analyze_login_pattern(user_id: str, days: int = 7) -> Dict:
    """
    로그인 패턴 분석 (비활동성)

    최근 N일 동안 활동한 날짜 수를 계산

    Args:
        user_id: 마스토돈 유저 ID
        days: 조회 기간 (일)

    Returns:
        Dict: 분석 결과
    """
    try:
        with get_mastodon_db() as conn:
            cursor = conn.cursor()

            # 최근 N일 동안 활동한 날짜 수
            cursor.execute("""
                SELECT COUNT(DISTINCT DATE(created_at)) as active_days
                FROM statuses
                WHERE account_id = %s
                AND created_at > NOW() - INTERVAL '%s days'
            """, (user_id, days))

            result = cursor.fetchone()
            active_days = result[0] if result else 0
            login_rate = active_days / days if days > 0 else 0.0

            # 비활동 기준값
            inactive_threshold = float(get_setting('inactive_threshold', '0.5'))

            return {
                'active_days': active_days,
                'login_rate': login_rate,
                'is_inactive': login_rate < inactive_threshold
            }

    except Exception as e:
        logger.error(f'로그인 패턴 분석 오류 (user_id={user_id}): {e}')
        return {
            'active_days': 0,
            'login_rate': 0.0,
            'is_inactive': False
        }


def analyze_all_users_social() -> None:
    """
    전체 사용자 사회성 분석 (매일 4시 자동 실행)

    대화 상대 분석 + 로그인 패턴 분석 결과를 user_stats에 저장
    분석 결과를 economy DB에 기록합니다.
    """
    logger.info('사회성 분석 시작')

    with get_economy_db() as conn:
        cursor = conn.cursor()

        # 일반 멤버 사용자 조회
        cursor.execute("""
            SELECT mastodon_id, username
            FROM users
            WHERE role = 'user'
        """)
        users = cursor.fetchall()

        for user in users:
            user_id = user['mastodon_id']
            username = user['username']

            logger.debug(f'사회성 분석 중: {username}')

            # 대화 상대 분석 (48시간)
            conversation_data = analyze_conversation_partners(user_id, 48)

            # 로그인 패턴 분석 (7일)
            login_data = analyze_login_pattern(user_id, 7)

            # user_stats에 저장
            cursor.execute("""
                INSERT INTO user_stats (
                    user_id,
                    unique_conversation_partners,
                    total_replies_sent,
                    top_partner_id,
                    top_partner_count,
                    top_partner_ratio,
                    active_days_7d,
                    login_rate_7d,
                    is_isolated,
                    is_inactive,
                    is_biased
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                conversation_data['unique_partners'],
                conversation_data['total_replies'],
                conversation_data['top_partner_id'],
                conversation_data['top_partner_count'],
                conversation_data['top_partner_ratio'],
                login_data['active_days'],
                login_data['login_rate'],
                conversation_data['is_isolated'],
                login_data['is_inactive'],
                conversation_data['is_biased']
            ))

            # 문제 발견 시 로그 출력
            if conversation_data['is_isolated']:
                logger.warning(f'고립 위험: {username} - 대화 상대 {conversation_data["unique_partners"]}명')
            if conversation_data['is_biased']:
                logger.warning(f'편향 위험: {username} - 특정인 {conversation_data["top_partner_ratio"]*100:.1f}%')
            if login_data['is_inactive']:
                logger.warning(f'비활동성: {username} - 7일 중 {login_data["active_days"]}일 활동')

    logger.info('사회성 분석 완료')


# ============================================================================
# 경고 발송 (관리자 호출)
# ============================================================================

def send_warning_dm(mastodon: Mastodon, user_id: str, username: str,
                   warning_type: str, message: str, admin_name: str = 'system') -> bool:
    """
    경고 DM 발송 (관리자 웹에서 호출)

    Args:
        mastodon: Mastodon 클라이언트
        user_id: 마스토돈 유저 ID
        username: 유저명
        warning_type: 경고 유형 (activity/isolation/bias/inactive 등)
        message: 경고 메시지
        admin_name: 관리자 이름

    Returns:
        bool: 성공 여부
    """
    try:
        # DM 발송
        send_dm(mastodon, username, message)

        # warnings 테이블에 기록
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO warnings
                (user_id, warning_type, message, dm_sent, admin_name)
                VALUES (?, ?, ?, 1, ?)
            """, (user_id, warning_type, message, admin_name))

        logger.info(f'경고 발송: {username} - {warning_type}')
        return True

    except Exception as e:
        logger.error(f'경고 발송 오류 (user_id={user_id}): {e}')
        return False


def get_warning_count(user_id: str, days: int = 30) -> int:
    """
    최근 N일 경고 횟수 조회

    Args:
        user_id: 마스토돈 유저 ID
        days: 조회 기간 (일)

    Returns:
        int: 경고 횟수
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM warnings
            WHERE user_id = ?
            AND timestamp > datetime('now', '-{} days')
        """.format(days), (user_id,))
        result = cursor.fetchone()
        return result['count'] if result else 0
