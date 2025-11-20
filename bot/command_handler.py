"""
봇 명령어 처리

멘션 명령어를 파싱하고 DM으로 응답합니다.
"""
from datetime import datetime, timedelta
from mastodon import Mastodon
from .database import (
    get_economy_db,
    get_or_create_user,
    get_user_balance,
    add_transaction,
    invalidate_user_cache
)
from .utils import (
    setup_logger,
    send_dm,
    favorite_status,
    format_currency,
    parse_mention_command,
    truncate_text
)

logger = setup_logger('bot.command_handler')


def handle_command(mastodon: Mastodon, notification: dict) -> None:
    """
    명령어 처리 메인 함수

    Args:
        mastodon: Mastodon 클라이언트
        notification: 멘션 알림 데이터
    """
    try:
        status = notification['status']
        account = status['account']
        content = status['content']

        user_id = str(account['id'])
        username = account['acct']

        # 사용자 확인/생성 (Lazy Creation)
        get_or_create_user(user_id, username, account.get('display_name'))

        # 명령어 파싱
        from .utils import sanitize_html
        clean_content = sanitize_html(content)
        command, args = parse_mention_command(clean_content)

        logger.info(f'명령어 수신: {username} - {command} {args}')

        # 명령어 라우팅
        if command in ['내재화', '잔액', 'balance']:
            cmd_balance(mastodon, user_id, username)

        elif command in ['상점', 'shop', '아이템']:
            cmd_shop(mastodon, user_id, username)

        elif command in ['구매', 'buy']:
            cmd_purchase(mastodon, user_id, username, status['id'], args)

        elif command in ['내아이템', 'inventory', '인벤토리']:
            cmd_inventory(mastodon, user_id, username)

        elif command in ['휴식', 'vacation']:
            cmd_vacation(mastodon, user_id, username, args)

        elif command in ['일정', 'schedule', 'calendar']:
            cmd_schedule(mastodon, user_id, username, args)

        elif command in ['공지', 'notice', 'announcement']:
            cmd_notice(mastodon, user_id, username)

        elif command in ['도움말', 'help', 'commands', '명령어']:
            cmd_help(mastodon, user_id, username)

        else:
            # 알 수 없는 명령어
            send_dm(mastodon, username,
                   f"알 수 없는 명령어입니다: {command}\n멘션 도움말을 참고해주세요.")

    except Exception as e:
        logger.error(f'명령어 처리 오류: {e}', exc_info=True)


# ============================================================================
# 명령어 핸들러
# ============================================================================

def cmd_balance(mastodon: Mastodon, user_id: str, username: str) -> None:
    """내재화 - 본인 재화 조회"""
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance, total_earned, total_spent FROM users WHERE mastodon_id = ?",
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            send_dm(mastodon, username, "등록된 사용자가 아닙니다.")
            return

        message = f"""※ 재화 정보

현재 잔액: {format_currency(user['balance'])}
총 획득: {format_currency(user['total_earned'])}
총 사용: {format_currency(user['total_spent'])}"""

        send_dm(mastodon, username, message)
        logger.info(f'잔액 조회: {username} - {user["balance"]}코인')


def cmd_shop(mastodon: Mastodon, user_id: str, username: str) -> None:
    """상점 - 구매 가능한 아이템 목록"""
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, price, description, category
            FROM items
            WHERE is_active = 1
            ORDER BY category, price
        """)
        items = cursor.fetchall()

        if not items:
            send_dm(mastodon, username, "현재 판매 중인 아이템이 없습니다.")
            return

        # 카테고리별 그룹핑
        categories = {}
        for item in items:
            cat = item['category'] or '기타'
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        # 메시지 생성
        message = "※ 상점 아이템 목록\n\n"
        for category, category_items in categories.items():
            message += f"[{category}]\n"
            for item in category_items:
                desc = f" - {item['description']}" if item['description'] else ""
                message += f"• {item['name']}: {format_currency(item['price'])}{desc}\n"
            message += "\n"

        message += "구매: 멘션 구매 [아이템명]"

        send_dm(mastodon, username, truncate_text(message))
        logger.info(f'상점 조회: {username}')


def cmd_purchase(mastodon: Mastodon, user_id: str, username: str,
                status_id: str, args: list) -> None:
    """구매 - 아이템 구매"""
    if not args:
        send_dm(mastodon, username, "아이템 이름을 입력해주세요.\n예: 멘션 구매 아이템1")
        return

    item_name = ' '.join(args)

    with get_economy_db() as conn:
        cursor = conn.cursor()

        # 아이템 조회
        cursor.execute("""
            SELECT id, name, price
            FROM items
            WHERE name = ? AND is_active = 1
        """, (item_name,))
        item = cursor.fetchone()

        if not item:
            send_dm(mastodon, username, f"'{item_name}' 아이템을 찾을 수 없습니다.")
            return

        # 잔액 확인
        balance = get_user_balance(user_id)
        if balance < item['price']:
            send_dm(mastodon, username,
                   f"재화가 부족합니다.\n필요: {format_currency(item['price'])}\n보유: {format_currency(balance)}")
            return

        # 구매 처리
        try:
            # 재화 차감
            add_transaction(
                user_id=user_id,
                transaction_type='purchase',
                amount=-item['price'],
                item_id=item['id'],
                description=f"{item['name']} 구매"
            )

            # 인벤토리 추가
            cursor.execute("""
                INSERT INTO inventory (user_id, item_id, quantity)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + 1
            """, (user_id, item['id']))

            # 캐시 무효화
            from .utils import invalidate_user_cache
            invalidate_user_cache(user_id)

            # 성공: 멘션 좋아요
            favorite_status(mastodon, status_id)

            # DM 발송
            new_balance = balance - item['price']
            send_dm(mastodon, username,
                   f"✓ 구매 완료!\n\n{item['name']} 구매 완료\n남은 재화: {format_currency(new_balance)}")

            logger.info(f'구매 성공: {username} - {item["name"]} ({item["price"]}코인)')

        except Exception as e:
            logger.error(f'구매 오류: {username} - {item_name}: {e}')
            send_dm(mastodon, username, "구매 처리 중 실패가 발생했습니다.")


def cmd_inventory(mastodon: Mastodon, user_id: str, username: str) -> None:
    """내아이템 - 보유 아이템 목록"""
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.name, inv.quantity, inv.acquired_at
            FROM inventory inv
            JOIN items i ON inv.item_id = i.id
            WHERE inv.user_id = ?
            ORDER BY inv.acquired_at DESC
        """, (user_id,))
        items = cursor.fetchall()

        if not items:
            send_dm(mastodon, username, "보유 중인 아이템이 없습니다.")
            return

        message = "○ 내 아이템\n\n"
        for item in items:
            acquired = datetime.fromisoformat(item['acquired_at']).strftime('%Y-%m-%d')
            quantity_text = f" x{item['quantity']}" if item['quantity'] > 1 else ""
            message += f"• {item['name']}{quantity_text} ({acquired})\n"

        send_dm(mastodon, username, message)
        logger.info(f'인벤토리 조회: {username}')


def cmd_vacation(mastodon: Mastodon, user_id: str, username: str, args: list) -> None:
    """휴식 - 휴식 신청/취소"""
    if not args:
        send_dm(mastodon, username,
               "휴식 기간을 입력해주세요.\n신청: 멘션 휴식 7\n취소: 멘션 휴식 취소")
        return

    if args[0] in ['취소', 'cancel', 'off']:
        # 휴식 취소
        with get_economy_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM vacation
                WHERE user_id = ?
                AND DATE('now') BETWEEN start_date AND end_date
            """, (user_id,))

            if cursor.rowcount > 0:
                send_dm(mastodon, username, "휴식이 취소되었습니다.")
                logger.info(f'휴식 취소: {username}')
            else:
                send_dm(mastodon, username, "진행 중인 휴식이 없습니다.")
        return

    # 휴식 신청
    try:
        days = int(args[0])
        if days <= 0:
            send_dm(mastodon, username, "휴식 기간은 1일 이상이어야 합니다.")
            return

        # 최대 휴식 기간 확인
        from .database import get_setting
        max_days = int(get_setting('max_vacation_days', '90'))
        if days > max_days:
            send_dm(mastodon, username, f"최대 휴식 기간은 {max_days}일입니다.")
            return

        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days - 1)  # N일 (당일 포함)

        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 기존 휴식 삭제
            cursor.execute("""
                DELETE FROM vacation
                WHERE user_id = ?
                AND end_date >= DATE('now')
            """, (user_id,))

            # 새 휴식 신청
            cursor.execute("""
                INSERT INTO vacation (user_id, start_date, end_date, reason, approved, registered_by)
                VALUES (?, ?, ?, ?, 1, 'self')
            """, (user_id, start_date, end_date, f'{days}일 휴식'))

            send_dm(mastodon, username,
                   f"휴식 신청 완료\n\n기간: {start_date.strftime('%m/%d')} ~ {end_date.strftime('%m/%d')} ({days}일)")

            logger.info(f'휴식 신청: {username} - {days}일')

    except ValueError:
        send_dm(mastodon, username, "숫자로 일수를 입력해주세요.\n예: 멘션 휴식 7")


def cmd_schedule(mastodon: Mastodon, user_id: str, username: str, args: list) -> None:
    """일정 - 일정 조회"""
    # 기간 설정
    if args and args[0] in ['이번달', 'month']:
        # 이번 달 전체
        today = datetime.now()
        start_date = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month.replace(day=1) - timedelta(days=1)
    elif args and args[0] in ['다음주', 'nextweek']:
        # 7~14일 이후
        start_date = datetime.now() + timedelta(days=7)
        end_date = start_date + timedelta(days=7)
    else:
        # 기본: 오늘부터 향후 30일 (최대 +30일)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)

    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, event_date, end_date, event_type, is_global_vacation
            FROM calendar_events
            WHERE event_date BETWEEN ? AND ?
            ORDER BY event_date
        """, (start_date.date(), end_date.date()))
        events = cursor.fetchall()

        if not events:
            send_dm(mastodon, username, "예정된 일정이 없습니다.")
            return

        message = f"※ 일정 ({start_date.strftime('%m/%d')} ~ {end_date.strftime('%m/%d')})\n\n"

        for event in events:
            event_date = datetime.fromisoformat(event['event_date']).strftime('%m/%d (%a)')
            icon = "○휴" if event['is_global_vacation'] else {
                'event': '○행',
                'holiday': '○휴',
                'notice': '※공'
            }.get(event['event_type'], '※공')

            message += f"• {event_date} {icon} {event['title']}\n"

        send_dm(mastodon, username, message)
        logger.info(f'일정 조회: {username}')


def cmd_notice(mastodon: Mastodon, user_id: str, username: str) -> None:
    """공지 - 최근 공지 및 일정"""
    with get_economy_db() as conn:
        cursor = conn.cursor()

        # 최근 공지 3개 (예약 발송 포함)
        cursor.execute("""
            SELECT content, scheduled_at
            FROM scheduled_posts
            WHERE post_type = 'announcement' AND is_public = 1
            ORDER BY scheduled_at DESC
            LIMIT 3
        """)
        notices = cursor.fetchall()

        # 가까운 일정 (7일 이내)
        cursor.execute("""
            SELECT title, event_date, event_type
            FROM calendar_events
            WHERE event_date BETWEEN DATE('now') AND DATE('now', '+7 days')
            ORDER BY event_date
        """)
        events = cursor.fetchall()

        message = "※ 공지 및 소식\n\n"

        if notices:
            message += "[최근 공지]\n"
            for notice in notices:
                date = datetime.fromisoformat(notice['scheduled_at']).strftime('%Y-%m-%d')
                # content 첫 50자만 표시
                from .utils import sanitize_html
                content_preview = sanitize_html(notice['content'])[:50]
                message += f"• {date}: {content_preview}...\n"
            message += "\n"

        if events:
            message += "[가까운 일정] (7일 이내)\n"
            for event in events:
                date = datetime.fromisoformat(event['event_date']).strftime('%m/%d (%a)')
                icon = {'event': '○행', 'holiday': '○휴', 'notice': '※공'}.get(event['event_type'], '※공')
                message += f"• {date} {icon} {event['title']}\n"

        if not notices and not events:
            message += "최근 공지나 일정이 없습니다."

        send_dm(mastodon, username, truncate_text(message))
        logger.info(f'공지 조회: {username}')


def cmd_help(mastodon: Mastodon, user_id: str, username: str) -> None:
    """도움말 - 명령어 목록"""
    message = """○ 봇 명령어 안내

[재화 및 아이템]
• 멘션 내재화 - 본인 재화 조회
• 멘션 상점 - 아이템 목록
• 멘션 구매 [아이템명] - 아이템 구매
• 멘션 내아이템 - 보유 아이템 조회

[휴가 및 일정]
• 멘션 휴가 N - N일 휴가 신청
• 멘션 휴가 취소 - 휴가 취소

[정보 조회]
• 멘션 일정 - 이번 달 일정
• 멘션 공지 - 최근 공지 및 소식
• 멘션 도움말 - 이 도움말 표시

모든 응답은 DM으로 전송됩니다."""

    send_dm(mastodon, username, message)
    logger.info(f'도움말 조회: {username}')
