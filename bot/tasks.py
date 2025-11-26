"""
Celery Tasks

크론 스케줄링:
- 재화 정산: 매일 4시, 16시
- 출석 트윗 발행: 매일 10시
- 소셜 분석: 매일 4시
- 활동량 체크: 매일 4시, 16시
"""
from celery import Celery
from celery.schedules import crontab
from datetime import datetime

# Celery 앱 생성
app = Celery('witch_bot')
app.config_from_object('bot.celeryconfig')

# 스케줄 설정
app.conf.beat_schedule = {
    # 재화 정산 (4시, 16시)
    'settle-rewards-4am': {
        'task': 'bot.tasks.settle_rewards_task',
        'schedule': crontab(hour=4, minute=0),
    },
    'settle-rewards-4pm': {
        'task': 'bot.tasks.settle_rewards_task',
        'schedule': crontab(hour=16, minute=0),
    },

    # 출석 트윗 발행 (10시)
    'post-attendance-10am': {
        'task': 'bot.tasks.post_attendance_task',
        'schedule': crontab(hour=10, minute=0),
    },

    # 소셜 분석 (4시)
    'analyze-social-4am': {
        'task': 'bot.tasks.analyze_social_task',
        'schedule': crontab(hour=4, minute=0),
    },

    # 활동량 체크 (4시, 16시)
    'check-activity-4am': {
        'task': 'bot.tasks.check_activity_task',
        'schedule': crontab(hour=4, minute=0),
    },
    'check-activity-4pm': {
        'task': 'bot.tasks.check_activity_task',
        'schedule': crontab(hour=16, minute=0),
    },

    # 예약 포스트 처리 (매분)
    'process-scheduled-posts': {
        'task': 'bot.tasks.process_scheduled_posts_task',
        'schedule': crontab(), # 매분 실행
    },
}


# ============================================================================
# Tasks
# ============================================================================

@app.task(name='bot.tasks.process_scheduled_posts_task')
def process_scheduled_posts_task():
    """예약된 공지 및 스토리를 게시하는 Task"""
    from bot.database import (
        get_due_scheduled_posts, update_scheduled_post_status,
        get_due_story_posts, update_story_post_status
    )
    from bot.utils import setup_logger, create_mastodon_client
    import os

    logger = setup_logger('celery.scheduled_posts')
    logger.info('예약 포스트 처리 Task 시작')
    
    admin_token = os.getenv('BOT_ACCESS_TOKEN')
    story_token = os.getenv('STORY_ACCESS_TOKEN')
    supervisor_token = os.getenv('SUPERVISOR_ACCESS_TOKEN')

    clients = {
        'announcement': create_mastodon_client(admin_token) if admin_token else None,
        'story': create_mastodon_client(story_token) if story_token else None,
        'admin_notice': create_mastodon_client(supervisor_token) if supervisor_token else None,
    }

    # 1. 일반 예약 포스트 처리 (공지, 관리자 알림 등)
    due_posts = get_due_scheduled_posts()
    for post in due_posts:
        post_type = post.get('post_type', 'announcement')
        client = clients.get(post_type)

        if not client:
            logger.warning(f"{post_type} 타입 포스트를 처리할 클라이언트가 없습니다. (토큰 부재)")
            continue

        logger.info(f"{post_type} 게시 시도: {post['id']} - {post['content'][:30]}")
        try:
            status = client.status_post(
                status=post['content'],
                visibility=post['visibility']
            )
            update_scheduled_post_status(post['id'], 'published', status['id'])
            logger.info(f"{post_type} 게시 성공: {post['id']}")
        except Exception as e:
            logger.error(f"{post_type} 게시 실패: {post['id']} - {e}", exc_info=True)
            update_scheduled_post_status(post['id'], 'failed', error_message=str(e))

    # 2. 스토리 포스트 처리 (별도 테이블)
    story_client = clients.get('story')
    if story_client:
        due_story_posts = get_due_story_posts()
        for post in due_story_posts:
            logger.info(f"스토리 포스트 게시 시도: {post['id']} - {post['content'][:30]}")
            try:
                status = story_client.status_post(status=post['content'])
                update_story_post_status(post['id'], 'published', status['id'])
                logger.info(f"스토리 포스트 게시 성공: {post['id']}")
            except Exception as e:
                logger.error(f"스토리 포스트 게시 실패: {post['id']} - {e}", exc_info=True)
                update_story_post_status(post['id'], 'failed', error_message=str(e))
    else:
        logger.warning("스토리 토큰이 없어 스토리 포스트를 처리할 수 없습니다.")
    
    logger.info('예약 포스트 처리 Task 종료')
    return {'status': 'success', 'timestamp': datetime.now().isoformat()}



@app.task(name='bot.tasks.settle_rewards_task')
def settle_rewards_task():
    """재화 정산 Task"""
    from bot.reward_bot import settle_rewards
    from bot.utils import setup_logger

    logger = setup_logger('celery.settle_rewards')
    logger.info('재화 정산 Task 시작')

    try:
        result = settle_rewards()
        logger.info(f'재화 정산 완료: {result}')
        return result
    except Exception as e:
        logger.error(f'재화 정산 실패: {e}', exc_info=True)
        raise


@app.task(name='bot.tasks.post_attendance_task')
def post_attendance_task():
    """출석 트윗 발행 Task"""
    from bot.reward_bot import post_attendance_tweet
    from bot.utils import setup_logger

    logger = setup_logger('celery.post_attendance')
    logger.info('출석 트윗 Task 시작')

    try:
        result = post_attendance_tweet()
        logger.info(f'출석 트윗 완료: {result}')
        return result
    except Exception as e:
        logger.error(f'출석 트윗 실패: {e}', exc_info=True)
        raise


@app.task(name='bot.tasks.analyze_social_task')
def analyze_social_task():
    """소셜 분석 Task"""
    from bot.activity_checker import analyze_all_users_social
    from bot.utils import setup_logger

    logger = setup_logger('celery.analyze_social')
    logger.info('소셜 분석 Task 시작')

    try:
        analyze_all_users_social()
        logger.info('소셜 분석 완료')
        return {'status': 'success', 'timestamp': datetime.now().isoformat()}
    except Exception as e:
        logger.error(f'소셜 분석 실패: {e}', exc_info=True)
        raise


@app.task(name='bot.tasks.check_activity_task')
def check_activity_task():
    """활동량 체크 Task"""
    from bot.activity_checker import check_all_users_activity
    from bot.utils import setup_logger

    logger = setup_logger('celery.check_activity')
    logger.info('활동량 체크 Task 시작')

    try:
        insufficient_users = check_all_users_activity()
        logger.info(f'활동량 체크 완료: {len(insufficient_users)}명 미달')
        return {
            'status': 'success',
            'insufficient_count': len(insufficient_users),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f'활동량 체크 실패: {e}', exc_info=True)
        raise


# ============================================================================
# 수동 실행용 Task
# ============================================================================

@app.task(name='bot.tasks.send_warning_task')
def send_warning_task(user_id: str, username: str, warning_type: str,
                     message: str, admin_name: str = 'admin'):
    """
    경고 발송 Task (관리자 웹에서 호출)

    Args:
        user_id: 마스토돈 계정 ID
        username: 유저명
        warning_type: 경고 타입
        message: 경고 메시지
        admin_name: 관리자 이름
    """
    from bot.activity_checker import send_warning_dm
    from bot.utils import setup_logger, create_mastodon_client

    logger = setup_logger('celery.send_warning')
    logger.info(f'경고 발송 Task: {username} ({warning_type})')

    try:
        mastodon = create_mastodon_client()
        success = send_warning_dm(mastodon, user_id, username, warning_type, message, admin_name)

        if success:
            logger.info(f'경고 발송 성공: {username}')
            return {'status': 'success', 'user_id': user_id}
        else:
            logger.error(f'경고 발송 실패: {username}')
            return {'status': 'failed', 'user_id': user_id}

    except Exception as e:
        logger.error(f'경고 발송 오류: {e}', exc_info=True)
        raise
