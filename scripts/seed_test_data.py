#!/usr/bin/env python3
"""
테스트 데이터 생성 스크립트
API 테스팅을 위한 더미 데이터를 생성합니다.
"""
import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta, time

# 프로젝트 루트 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 데이터베이스 경로
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'economy.db')


# ============================================================================
# 테스트 데이터 상수
# ============================================================================

# 한국어 이름 샘플
KOREAN_SURNAMES = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '류', '전']
KOREAN_NAMES = ['민준', '서연', '하준', '지우', '도윤', '서현', '시우', '수아', '예준', '지아', '주원', '채원', '지호', '다은', '준서', '은우', '현우', '채은', '승우', '하은']

# 샘플 경고 메시지
WARNING_MESSAGES = [
    "활동량 부족 경고: 최근 48시간 동안 활동량이 기준 미달입니다.",
    "연속 경고: 이전 경고 이후에도 활동량이 개선되지 않았습니다.",
    "최종 경고: 재화 차감 전 마지막 경고입니다.",
    "활동량 미달: 답글 수가 최소 기준에 도달하지 못했습니다.",
    "휴가 미신청 경고: 활동이 없으나 휴가 신청이 없습니다."
]

WARNING_TYPES = ['activity_low', 'activity_warning', 'activity_final', 'vacation_missing']

# 샘플 거래 내역 설명
TRANSACTION_DESCRIPTIONS = [
    "활동량 보상 지급",
    "이벤트 참여 보상",
    "관리자 수동 지급",
    "경고로 인한 차감",
    "아이템 구매",
    "정산 보상",
    "특별 보너스",
    "출석 보상",
    "미션 완료 보상",
    "휴가 복귀 보상"
]

# 샘플 이벤트
EVENT_TITLES = [
    "🎄 크리스마스 특별 이벤트",
    "🎉 신년 맞이 이벤트",
    "🌸 봄맞이 이벤트",
    "☀️ 여름 휴가 이벤트",
    "🍂 가을 감사제",
    "❄️ 겨울 축제",
    "🎃 할로윈 이벤트",
    "💝 발렌타인데이 이벤트",
    "🌟 주년 기념 이벤트",
    "🎊 창립 기념일"
]

EVENT_DESCRIPTIONS = [
    "특별한 날을 함께 축하해요! 이벤트 기간 동안 다양한 보상이 제공됩니다.",
    "이벤트 참여자 전원에게 특별 보상을 드립니다.",
    "기간 내 활동량 달성 시 추가 보너스가 지급됩니다.",
    "커뮤니티 전체가 참여하는 특별 이벤트입니다.",
    "제한 시간 내 미션을 완료하고 보상을 받아가세요!"
]

EVENT_TYPES = ['general', 'seasonal', 'special', 'competition', 'vacation']

# 샘플 아이템
ITEMS = [
    ("🎨 프로필 테마: 벚꽃", "프로필을 벚꽃 테마로 꾸밀 수 있습니다", 5000, "cosmetic"),
    ("🌙 프로필 테마: 밤하늘", "프로필을 밤하늘 테마로 꾸밀 수 있습니다", 5000, "cosmetic"),
    ("⭐ 닉네임 색상: 골드", "닉네임을 골드 색상으로 변경합니다", 3000, "cosmetic"),
    ("💎 닉네임 색상: 다이아몬드", "닉네임을 다이아몬드 색상으로 변경합니다", 8000, "cosmetic"),
    ("🔖 커스텀 배지", "자신만의 배지를 만들 수 있습니다", 10000, "badge"),
    ("🏆 VIP 배지", "VIP 전용 배지", 15000, "badge"),
    ("📝 긴 글 작성권", "2000자 제한을 4000자로 확장", 7000, "utility"),
    ("🖼️ 이미지 슬롯 +5", "이미지 첨부 개수 +5", 6000, "utility"),
    ("🎁 랜덤 박스", "랜덤한 아이템을 획득합니다", 2000, "lootbox"),
    ("💰 재화 2배 쿠폰 (7일)", "7일간 재화 획득량 2배", 12000, "boost"),
    ("🍀 행운의 부적", "이벤트 당첨 확률 증가", 4000, "utility"),
    ("🎪 이벤트 우선권", "이벤트에 우선 참여 가능", 5000, "utility"),
    ("📢 공지 강조권", "자신의 글을 24시간 동안 강조 표시", 3000, "utility"),
    ("🎭 익명 글쓰기권", "익명으로 글을 작성할 수 있습니다", 2500, "utility"),
    ("🌈 레인보우 테마", "프로필을 레인보우 테마로 변경", 8000, "cosmetic")
]

# 관리자 이름 샘플
ADMIN_NAMES = ["마녀봇", "운영진A", "운영진B", "시스템관리자", "총괄관리자"]

# 관리자 로그 액션 타입
ADMIN_ACTION_TYPES = [
    ('currency_adjust', '재화 조정'),
    ('warning_send', '경고 발송'),
    ('role_change', '권한 변경'),
    ('vacation_approve', '휴가 승인'),
    ('vacation_reject', '휴가 거부'),
    ('event_create', '이벤트 생성'),
    ('event_update', '이벤트 수정'),
    ('item_create', '아이템 생성'),
    ('settings_update', '설정 변경'),
    ('user_ban', '사용자 차단')
]

# 기숙사
DORMITORIES = ['A동', 'B동', 'C동', 'D동', 'E동', None]


# ============================================================================
# 유틸리티 함수
# ============================================================================

def random_datetime(start_days_ago=90, end_days_ago=0):
    """랜덤한 datetime 생성 (과거 N일 ~ M일 사이)"""
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def random_korean_name():
    """랜덤 한국어 이름 생성"""
    return random.choice(KOREAN_SURNAMES) + random.choice(KOREAN_NAMES)


def random_mastodon_id():
    """랜덤 Mastodon 사용자 ID 생성 (10-13자리 숫자)"""
    return str(random.randint(1000000000, 9999999999999))


def random_mastodon_username():
    """랜덤 Mastodon 사용자명 생성"""
    prefixes = ['witch', 'magic', 'star', 'moon', 'sun', 'cloud', 'rain', 'snow', 'wind', 'fire']
    suffixes = ['lover', 'hunter', 'master', 'keeper', 'walker', 'dreamer', 'seeker', 'maker']
    return random.choice(prefixes) + random.choice(suffixes) + str(random.randint(100, 999))


def random_time():
    """랜덤 시간 생성"""
    return time(random.randint(0, 23), random.randint(0, 59))


# ============================================================================
# 데이터 생성 함수
# ============================================================================

def clear_test_data(conn):
    """기존 테스트 데이터 삭제 (clean slate)"""
    print("\n🗑️  기존 데이터 삭제 중...")
    cursor = conn.cursor()

    # 순서 중요: 외래 키 제약 조건 때문에 역순으로 삭제
    tables = ['admin_logs', 'items', 'calendar_events', 'vacation', 'warnings', 'transactions', 'users']

    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        count = cursor.rowcount
        print(f"   ✓ {table}: {count}개 삭제")

    conn.commit()
    print("✅ 기존 데이터 삭제 완료\n")


def seed_users(conn, count=15):
    """사용자 테스트 데이터 생성"""
    print(f"👥 사용자 {count}명 생성 중...")
    cursor = conn.cursor()
    users = []

    for i in range(count):
        mastodon_id = random_mastodon_id()
        username = random_mastodon_username()
        display_name = random_korean_name()

        # 역할: 80% 일반, 15% 우대, 5% 관리자
        role_rand = random.random()
        if role_rand < 0.8:
            role = 'normal'
        elif role_rand < 0.95:
            role = 'preferred'
        else:
            role = 'admin'

        # 기숙사
        dormitory = random.choice(DORMITORIES)

        # 재화: 0 ~ 50000 사이 랜덤
        balance = random.randint(0, 50000)
        total_earned = random.randint(balance, balance + 50000)
        total_spent = total_earned - balance

        # 답글 수: 0 ~ 100
        reply_count = random.randint(0, 100)

        # 마지막 활동: 0~30일 전
        last_active = random_datetime(30, 0)

        # 마지막 체크: 마지막 활동 이후
        last_check = random_datetime(30, 0)

        # 가입일: 30~365일 전
        created_at = random_datetime(365, 30)

        cursor.execute("""
            INSERT INTO users (
                mastodon_id, username, display_name, role, dormitory,
                balance, total_earned, total_spent, reply_count,
                last_active, last_check, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mastodon_id, username, display_name, role, dormitory,
            balance, total_earned, total_spent, reply_count,
            last_active, last_check, created_at
        ))

        users.append({
            'mastodon_id': mastodon_id,
            'username': username,
            'display_name': display_name,
            'role': role,
            'balance': balance
        })

    conn.commit()
    print(f"✅ 사용자 {count}명 생성 완료\n")
    return users


def seed_transactions(conn, users, count=60):
    """거래 내역 테스트 데이터 생성"""
    print(f"💰 거래 내역 {count}개 생성 중...")
    cursor = conn.cursor()

    for i in range(count):
        user = random.choice(users)

        # 거래 타입: 70% 지급, 30% 차감
        if random.random() < 0.7:
            transaction_type = 'earn'
            amount = random.choice([100, 200, 300, 500, 1000, 2000, 5000])
        else:
            transaction_type = 'spend'
            amount = random.choice([100, 200, 500, 1000, 2000])

        description = random.choice(TRANSACTION_DESCRIPTIONS)

        # status_id: 50% 확률로 랜덤 status ID
        status_id = str(random.randint(1000000000000000000, 9999999999999999999)) if random.random() < 0.5 else None

        # item_id: 20% 확률로 아이템 구매
        item_id = random.randint(1, 15) if random.random() < 0.2 and transaction_type == 'spend' else None

        # admin_name: 30% 확률로 관리자 수동 조정
        admin_name = random.choice(ADMIN_NAMES) if random.random() < 0.3 else None

        timestamp = random_datetime(60, 0)

        cursor.execute("""
            INSERT INTO transactions (
                user_id, transaction_type, amount, status_id,
                item_id, description, admin_name, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user['mastodon_id'], transaction_type, amount, status_id, item_id, description, admin_name, timestamp))

    conn.commit()
    print(f"✅ 거래 내역 {count}개 생성 완료\n")


def seed_warnings(conn, users, count=12):
    """경고 테스트 데이터 생성"""
    print(f"⚠️  경고 {count}개 생성 중...")
    cursor = conn.cursor()

    for i in range(count):
        user = random.choice(users)
        warning_type = random.choice(WARNING_TYPES)
        check_period_hours = 48
        required_replies = 20
        actual_replies = random.randint(0, 19)
        message = random.choice(WARNING_MESSAGES)
        dm_sent = random.choice([True, False])
        admin_name = random.choice(ADMIN_NAMES)
        timestamp = random_datetime(30, 0)

        cursor.execute("""
            INSERT INTO warnings (
                user_id, warning_type, check_period_hours, required_replies,
                actual_replies, message, dm_sent, admin_name, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user['mastodon_id'], warning_type, check_period_hours, required_replies,
              actual_replies, message, dm_sent, admin_name, timestamp))

    conn.commit()
    print(f"✅ 경고 {count}개 생성 완료\n")


def seed_vacations(conn, users, count=8):
    """휴가 테스트 데이터 생성"""
    print(f"🏖️  휴가 {count}개 생성 중...")
    cursor = conn.cursor()

    for i in range(count):
        user = random.choice(users)

        # 휴가 기간: 과거, 현재, 미래 섞어서
        start_days_ago = random.randint(-30, 30)  # 음수면 미래
        duration = random.randint(3, 14)  # 3~14일

        if start_days_ago > 0:
            start_date = (datetime.now() - timedelta(days=start_days_ago)).date()
            end_date = (datetime.now() - timedelta(days=start_days_ago - duration)).date()
        else:
            start_date = (datetime.now() + timedelta(days=-start_days_ago)).date()
            end_date = (datetime.now() + timedelta(days=-start_days_ago + duration)).date()

        # 시작/종료 시간
        start_time = random_time().isoformat() if random.random() < 0.5 else None
        end_time = random_time().isoformat() if random.random() < 0.5 else None

        reason = random.choice([
            "개인 사정으로 인한 휴가",
            "여행",
            "시험 기간",
            "건강상의 이유",
            "가족 행사",
            "업무 과다로 인한 휴식",
            "학업 집중 기간"
        ])

        # 승인 여부: 80% 승인
        approved = random.random() < 0.8

        registered_by = random.choice(ADMIN_NAMES) if random.random() < 0.5 else user['username']

        created_at = random_datetime(60, 0)

        cursor.execute("""
            INSERT INTO vacation (
                user_id, start_date, start_time, end_date, end_time,
                reason, approved, registered_by, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user['mastodon_id'], start_date, start_time, end_date, end_time,
              reason, approved, registered_by, created_at))

    conn.commit()
    print(f"✅ 휴가 {count}개 생성 완료\n")


def seed_events(conn, count=7):
    """이벤트 테스트 데이터 생성"""
    print(f"🎉 이벤트 {count}개 생성 중...")
    cursor = conn.cursor()

    for i in range(count):
        title = random.choice(EVENT_TITLES)
        description = random.choice(EVENT_DESCRIPTIONS)

        # 이벤트 기간: 과거, 현재, 미래 섞어서
        start_days_ago = random.randint(-30, 60)  # 음수면 미래
        duration = random.randint(7, 30)  # 7~30일

        if start_days_ago > 0:
            event_date = (datetime.now() - timedelta(days=start_days_ago)).date()
            end_date = (datetime.now() - timedelta(days=start_days_ago - duration)).date()
        else:
            event_date = (datetime.now() + timedelta(days=-start_days_ago)).date()
            end_date = (datetime.now() + timedelta(days=-start_days_ago + duration)).date()

        # 시작/종료 시간
        start_time = random_time().isoformat() if random.random() < 0.3 else None
        end_time = random_time().isoformat() if random.random() < 0.3 else None

        # 이벤트 타입
        event_type = random.choice(EVENT_TYPES)

        # 전체 휴가 여부: 10% 확률
        is_global_vacation = random.random() < 0.1

        created_by = random.choice(ADMIN_NAMES)
        created_at = random_datetime(60, 0)
        updated_at = random_datetime(30, 0) if random.random() < 0.3 else created_at

        cursor.execute("""
            INSERT INTO calendar_events (
                title, description, event_date, start_time, end_date, end_time,
                event_type, is_global_vacation, created_by, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, description, event_date, start_time, end_date, end_time,
              event_type, is_global_vacation, created_by, created_at, updated_at))

    conn.commit()
    print(f"✅ 이벤트 {count}개 생성 완료\n")


def seed_items(conn):
    """아이템 테스트 데이터 생성"""
    print(f"🛍️  아이템 {len(ITEMS)}개 생성 중...")
    cursor = conn.cursor()

    for name, description, price, category in ITEMS:
        # 활성화 여부: 90% 활성화
        is_active = random.random() < 0.9

        # 이미지 URL: 50% 확률로 설정
        image_url = f"https://example.com/images/{name[:10]}.png" if random.random() < 0.5 else None

        created_at = random_datetime(90, 0)

        cursor.execute("""
            INSERT INTO items (name, description, price, category, image_url, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, description, price, category, image_url, is_active, created_at))

    conn.commit()
    print(f"✅ 아이템 {len(ITEMS)}개 생성 완료\n")


def seed_admin_logs(conn, users, count=40):
    """관리자 로그 테스트 데이터 생성"""
    print(f"📋 관리자 로그 {count}개 생성 중...")
    cursor = conn.cursor()

    for i in range(count):
        user = random.choice(users)
        admin_name = random.choice(ADMIN_NAMES)
        action_type, action_desc = random.choice(ADMIN_ACTION_TYPES)

        # 액션별 상세 정보
        if action_type == 'currency_adjust':
            amount = random.choice([100, 500, 1000, 2000, -500, -1000])
            details = f"{user['display_name']}에게 {amount:+,}원 조정"
        elif action_type == 'warning_send':
            details = f"{user['display_name']}에게 활동량 부족 경고 발송"
        elif action_type == 'role_change':
            new_role = random.choice(['normal', 'preferred', 'admin'])
            details = f"{user['display_name']}의 권한을 {new_role}로 변경"
        elif action_type == 'vacation_approve':
            details = f"{user['display_name']}의 휴가 신청 승인"
        elif action_type == 'vacation_reject':
            details = f"{user['display_name']}의 휴가 신청 거부"
        else:
            details = f"{action_desc}: {user['display_name']}"

        target_user = user['mastodon_id']
        timestamp = random_datetime(60, 0)

        cursor.execute("""
            INSERT INTO admin_logs (admin_name, action_type, target_user, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_name, action_type, target_user, details, timestamp))

    conn.commit()
    print(f"✅ 관리자 로그 {count}개 생성 완료\n")


# ============================================================================
# 메인 실행
# ============================================================================

def main():
    """메인 함수"""
    print("=" * 70)
    print("🌟 테스트 데이터 생성 스크립트")
    print("=" * 70)
    print(f"📁 DB 경로: {DB_PATH}")

    # DB 파일 존재 확인
    if not os.path.exists(DB_PATH):
        print(f"\n❌ 데이터베이스 파일이 없습니다: {DB_PATH}")
        print("먼저 init_db.py로 데이터베이스를 초기화하세요.")
        return 1

    # DB 연결
    conn = sqlite3.connect(DB_PATH)

    try:
        # 기존 데이터 삭제
        clear_test_data(conn)

        # 테스트 데이터 생성
        users = seed_users(conn, count=15)
        seed_transactions(conn, users, count=60)
        seed_warnings(conn, users, count=12)
        seed_vacations(conn, users, count=8)
        seed_events(conn, count=7)
        seed_items(conn)
        seed_admin_logs(conn, users, count=40)

        print("=" * 70)
        print("✅ 모든 테스트 데이터 생성 완료!")
        print("=" * 70)
        print("\n📊 생성된 데이터 요약:")

        # 테이블별 데이터 개수 확인
        cursor = conn.cursor()
        tables = ['users', 'transactions', 'warnings', 'vacation', 'calendar_events', 'items', 'admin_logs']

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count}개")

        print("\n🚀 이제 API 테스트를 시작할 수 있습니다!")
        print("   Flask 서버: python -m admin_web.app")
        print("   API 테스트: python scripts/test_all_api.py")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        conn.close()

    return 0


if __name__ == '__main__':
    exit(main())
