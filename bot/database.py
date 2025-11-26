"""
데이터베이스 유틸리티

SQLite (economy.db)와 PostgreSQL (Mastodon DB) 연결을 관리합니다.
Flask와 독립적으로 실행 가능한 봇에서도 사용할 수 있습니다.
"""
import os
import sqlite3
import psycopg2
from contextlib import contextmanager
from typing import Generator
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()


@contextmanager
def get_economy_db() -> Generator[sqlite3.Connection, None, None]:
    """
    SQLite economy.db 연결

    Yields:
        sqlite3.Connection: SQLite 데이터베이스 연결
    """
    db_path = os.getenv('DATABASE_PATH', 'economy.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_mastodon_db() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    PostgreSQL 마스토돈 DB 연결 (읽기 전용)

    봇에서 팔로우 이벤트 확인 등에 사용합니다.

    Yields:
        psycopg2.connection: PostgreSQL 데이터베이스 연결
    """
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', '5432')),
        database=os.getenv('POSTGRES_DB', 'mastodon'),
        user=os.getenv('POSTGRES_USER', 'mastodon'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
    )
    conn.set_session(readonly=True, autocommit=True)
    try:
        yield conn
    finally:
        conn.close()


def get_or_create_user(mastodon_id: str, username: str, display_name: str = None) -> tuple[bool, dict]:
    """
    사용자 조회 또는 자동 생성 (Lazy Creation)

    Args:
        mastodon_id: 마스토돈 유저 ID
        username: 유저명 (@아이디)
        display_name: 표시 이름

    Returns:
        tuple[bool, dict]: (새로 생성되었는지 여부, 사용자 정보)
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()

        # 사용자 조회
        cursor.execute(
            "SELECT * FROM users WHERE mastodon_id = ?",
            (mastodon_id,)
        )
        user = cursor.fetchone()

        if user:
            return (False, dict(user))

        # 사용자 생성
        cursor.execute("""
            INSERT INTO users (mastodon_id, username, display_name)
            VALUES (?, ?, ?)
        """, (mastodon_id, username, display_name))

        # 생성된 사용자 조회
        cursor.execute(
            "SELECT * FROM users WHERE mastodon_id = ?",
            (mastodon_id,)
        )
        new_user = cursor.fetchone()
        return (True, dict(new_user))


def add_transaction(user_id: str, transaction_type: str, amount: int,
                   status_id: str = None, item_id: int = None,
                   description: str = None, admin_name: str = None) -> int:
    """
    거래 내역을 기록하고 사용자 잔액을 업데이트합니다

    Args:
        user_id: 마스토돈 유저 ID
        transaction_type: 거래 유형 (reply/attendance/purchase/admin_adjust 등)
        amount: 금액 (양수: 수입, 음수: 지출)
        status_id: 마스토돈 status ID (관련 게시글 링크용)
        item_id: 아이템 ID (구매시)
        description: 설명
        admin_name: 관리자 이름 (admin_adjust시)

    Returns:
        int: 생성된 transaction ID
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()

        # 거래 기록 생성
        cursor.execute("""
            INSERT INTO transactions
            (user_id, transaction_type, amount, status_id, item_id, description, admin_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, transaction_type, amount, status_id, item_id, description, admin_name))

        transaction_id = cursor.lastrowid

        # 사용자 잔액 업데이트
        if amount > 0:
            cursor.execute("""
                UPDATE users
                SET balance = balance + ?,
                    total_earned = total_earned + ?
                WHERE mastodon_id = ?
            """, (amount, amount, user_id))
        else:
            cursor.execute("""
                UPDATE users
                SET balance = balance + ?,
                    total_spent = total_spent + ?
                WHERE mastodon_id = ?
            """, (amount, abs(amount), user_id))

        return transaction_id


def is_duplicate_transaction(status_id: str) -> bool:
    """
    중복 방지용: status_id로 이미 처리된 거래인지 확인

    Args:
        status_id: 마스토돈 status ID

    Returns:
        bool: 중복이면 True
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as count FROM transactions WHERE status_id = ?",
            (status_id,)
        )
        result = cursor.fetchone()
        return result['count'] > 0


def get_user_balance(user_id: str) -> int:
    """
    사용자 잔액 조회

    Args:
        user_id: 마스토돈 유저 ID

    Returns:
        int: 잔액 (사용자 없으면 0)
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance FROM users WHERE mastodon_id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        return user['balance'] if user else 0


def check_attendance(user_id: str, attendance_post_id: str) -> bool:
    """
    출석 체크: 이미 출석했는지 확인

    Args:
        user_id: 마스토돈 유저 ID
        attendance_post_id: 출석 게시글 ID

    Returns:
        bool: 이미 출석했으면 True
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM attendances
            WHERE user_id = ? AND attendance_post_id = ?
        """, (user_id, attendance_post_id))
        result = cursor.fetchone()
        return result['count'] > 0


def record_attendance(user_id: str, attendance_post_id: str, reward_amount: int) -> bool:
    """
    출석 기록 및 보상 지급

    Args:
        user_id: 마스토돈 유저 ID
        attendance_post_id: 출석 게시글 ID
        reward_amount: 보상 금액

    Returns:
        bool: 성공 여부
    """
    try:
        with get_economy_db() as conn:
            cursor = conn.cursor()

            # 출석 기록
            cursor.execute("""
                INSERT INTO attendances (user_id, attendance_post_id, reward_amount)
                VALUES (?, ?, ?)
            """, (user_id, attendance_post_id, reward_amount))

            # 출석 게시글 통계 업데이트
            cursor.execute("""
                UPDATE attendance_posts
                SET total_attendees = total_attendees + 1
                WHERE post_id = ?
            """, (attendance_post_id,))

            # 재화 지급
            add_transaction(
                user_id=user_id,
                transaction_type='attendance',
                amount=reward_amount,
                status_id=attendance_post_id,
                description='출석 체크 보상'
            )

            return True
    except sqlite3.IntegrityError:
        # UNIQUE constraint 위반 (이미 출석함)
        return False


def is_on_vacation(user_id: str) -> bool:
    """
    개인 휴가 상태인지 확인

    Args:
        user_id: 마스토돈 유저 ID

    Returns:
        bool: 휴가 중이면 True
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM vacation
            WHERE user_id = ?
            AND approved = 1
            AND DATE('now') BETWEEN start_date AND end_date
        """, (user_id,))
        result = cursor.fetchone()
        return result['count'] > 0


def is_global_vacation() -> bool:
    """
    전체 커뮤니티 휴가인지 확인

    Returns:
        bool: 전체 휴가면 True
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM calendar_events
            WHERE is_global_vacation = 1
            AND DATE('now') BETWEEN event_date AND COALESCE(end_date, event_date)
        """)
        result = cursor.fetchone()
        return result['count'] > 0


def get_setting(key: str, default: str = None) -> str:
    """
    설정값 조회

    Args:
        key: 설정 키
        default: 기본값

    Returns:
        str: 설정값 (없으면 default)
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result['value'] if result else default


def update_setting(key: str, value: str, updated_by: str = None) -> None:
    """
    설정값 업데이트

    Args:
        key: 설정 키
        value: 설정값
        updated_by: 수정자
    """
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE settings
            SET value = ?, updated_at = CURRENT_TIMESTAMP, updated_by = ?
            WHERE key = ?
        """, (value, updated_by, key))


def get_due_scheduled_posts() -> list:
    """발행 시간이 된 예약 공지 목록을 가져옵니다."""
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM scheduled_posts
            WHERE status = 'pending'
            AND scheduled_at <= datetime('now', 'localtime')
        """)
        return [dict(row) for row in cursor.fetchall()]

def update_scheduled_post_status(post_id: int, status: str, mastodon_post_id: str = None, error_message: str = None):
    """예약 공지의 상태를 업데이트합니다."""
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE scheduled_posts
            SET status = ?, mastodon_scheduled_id = ?, published_at = CASE WHEN ? = 'published' THEN datetime('now', 'localtime') ELSE NULL END
            WHERE id = ?
        """, (status, mastodon_post_id, status, post_id))

def get_due_story_posts() -> list:
    """발행 시간이 된 스토리 포스트 목록을 가져옵니다."""
    with get_economy_db() as conn:
        cursor = conn.cursor()
        # First, ensure parent story_event is active
        cursor.execute("""
            UPDATE story_events
            SET status = 'processing'
            WHERE status = 'pending' AND start_time <= datetime('now', 'localtime')
        """)
        
        cursor.execute("""
            SELECT sp.*
            FROM story_posts sp
            JOIN story_events se ON sp.event_id = se.id
            WHERE se.status = 'processing'
            AND sp.status = 'pending'
            AND sp.scheduled_at <= datetime('now', 'localtime')
        """)
        return [dict(row) for row in cursor.fetchall()]

def update_story_post_status(post_id: int, status: str, mastodon_post_id: str = None, error_message: str = None):
    """스토리 포스트의 상태를 업데이트합니다."""
    with get_economy_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE story_posts
            SET status = ?, mastodon_post_id = ?, published_at = CASE WHEN ? = 'published' THEN datetime('now', 'localtime') ELSE NULL END, error_message = ?
            WHERE id = ?
        """, (status, mastodon_post_id, status, error_message, post_id))


def transfer_item(sender_id: str, receiver_id: str, item_id: int, quantity: int) -> bool:
    """
    한 사용자에게서 다른 사용자에게로 아이템을 이전합니다.

    Args:
        sender_id: 보내는 사람의 Mastodon ID
        receiver_id: 받는 사람의 Mastodon ID
        item_id: 아이템 ID
        quantity: 수량

    Returns:
        성공 여부
    """
    if quantity <= 0:
        return False

    with get_economy_db() as conn:
        cursor = conn.cursor()
        
        # 1. 보내는 사람의 인벤토리 확인
        cursor.execute(
            "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?",
            (sender_id, item_id)
        )
        sender_inventory = cursor.fetchone()

        if not sender_inventory or sender_inventory['quantity'] < quantity:
            return False  # 아이템이 없거나 수량이 부족함

        # 2. 보내는 사람 인벤토리에서 차감
        new_quantity = sender_inventory['quantity'] - quantity
        if new_quantity > 0:
            cursor.execute(
                "UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?",
                (new_quantity, sender_id, item_id)
            )
        else:
            cursor.execute(
                "DELETE FROM inventory WHERE user_id = ? AND item_id = ?",
                (sender_id, item_id)
            )

        # 3. 받는 사람 인벤토리에 추가
        cursor.execute("""
            INSERT INTO inventory (user_id, item_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + excluded.quantity
        """, (receiver_id, item_id, quantity))

        return True


