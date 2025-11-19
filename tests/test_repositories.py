"""
Repository 레이어 테스트

UserRepository, TransactionRepository, ItemRepository 등을 테스트합니다.
"""
import pytest
from datetime import datetime
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository
from admin_web.repositories.item_repository import ItemRepository
from admin_web.repositories.vacation_repository import VacationRepository
from admin_web.repositories.warning_repository import WarningRepository


class TestUserRepository:
    """UserRepository 테스트"""

    def test_get_all_users(self, db_conn):
        """전체 유저 조회"""
        repo = UserRepository(db_conn)

        # 샘플 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, display_name, balance)
            VALUES ('user1', 'testuser1', 'Test User 1', 1000)
        """)
        db_conn.commit()

        users = repo.get_all()
        assert len(users) >= 1
        assert any(u['username'] == 'testuser1' for u in users)

    def test_get_user_by_id(self, db_conn):
        """ID로 유저 조회"""
        repo = UserRepository(db_conn)

        # 샘플 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, display_name, balance)
            VALUES ('user1', 'testuser1', 'Test User 1', 1000)
        """)
        db_conn.commit()

        user = repo.get_by_id('user1')
        assert user is not None
        assert user['username'] == 'testuser1'
        assert user['balance'] == 1000

    def test_create_user(self, db_conn):
        """유저 생성"""
        repo = UserRepository(db_conn)

        user_id = repo.create(
            mastodon_id='user2',
            username='testuser2',
            display_name='Test User 2'
        )

        assert user_id == 'user2'

        user = repo.get_by_id('user2')
        assert user['username'] == 'testuser2'
        assert user['balance'] == 0  # 기본값

    def test_update_user_balance(self, db_conn):
        """유저 잔액 업데이트"""
        repo = UserRepository(db_conn)

        # 유저 생성
        repo.create('user3', 'testuser3', 'Test User 3')

        # 잔액 업데이트
        success = repo.update_balance('user3', 5000)
        assert success is True

        user = repo.get_by_id('user3')
        assert user['balance'] == 5000


class TestTransactionRepository:
    """TransactionRepository 테스트"""

    def test_create_transaction(self, db_conn):
        """거래 생성"""
        # 유저 생성
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        repo = TransactionRepository(db_conn)

        transaction_id = repo.create(
            user_id='user1',
            transaction_type='reply',
            amount=100,
            description='테스트 거래'
        )

        assert transaction_id > 0

    def test_get_by_user(self, db_conn):
        """유저별 거래 내역 조회"""
        # 유저 생성
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        # 거래 추가
        db_conn.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount, description)
            VALUES ('user1', 'reply', 100, '테스트 거래')
        """)
        db_conn.commit()

        repo = TransactionRepository(db_conn)
        transactions = repo.get_by_user('user1')

        assert len(transactions) >= 1
        assert transactions[0]['user_id'] == 'user1'


class TestItemRepository:
    """ItemRepository 테스트"""

    def test_get_all_items(self, db_conn):
        """전체 아이템 조회"""
        repo = ItemRepository(db_conn)

        # 샘플 아이템 추가
        db_conn.execute("""
            INSERT INTO items (name, price, is_active)
            VALUES ('테스트 아이템', 500, 1)
        """)
        db_conn.commit()

        items = repo.get_all()
        assert len(items) >= 1

    def test_create_item(self, db_conn):
        """아이템 생성"""
        repo = ItemRepository(db_conn)

        item_id = repo.create(
            name='새 아이템',
            price=1000,
            description='테스트 아이템',
            category='기타'
        )

        assert item_id > 0

        item = repo.get_by_id(item_id)
        assert item['name'] == '새 아이템'
        assert item['price'] == 1000

    def test_update_item(self, db_conn):
        """아이템 업데이트"""
        repo = ItemRepository(db_conn)

        # 아이템 생성
        item_id = repo.create('아이템1', 500, '설명1')

        # 업데이트
        success = repo.update(item_id, name='수정된 아이템', price=600)
        assert success is True

        item = repo.get_by_id(item_id)
        assert item['name'] == '수정된 아이템'
        assert item['price'] == 600

    def test_delete_item(self, db_conn):
        """아이템 삭제 (비활성화)"""
        repo = ItemRepository(db_conn)

        # 아이템 생성
        item_id = repo.create('아이템1', 500, '설명1')

        # 삭제
        success = repo.delete(item_id)
        assert success is True

        item = repo.get_by_id(item_id)
        assert item['is_active'] == 0


class TestVacationRepository:
    """VacationRepository 테스트"""

    def test_create_vacation(self, db_conn):
        """휴가 생성"""
        # 유저 생성
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        repo = VacationRepository(db_conn)

        vacation_id = repo.create(
            user_id='user1',
            start_date='2025-01-01',
            end_date='2025-01-07',
            reason='테스트 휴가'
        )

        assert vacation_id > 0

    def test_get_active_vacations(self, db_conn):
        """활성 휴가 조회"""
        # 유저 생성
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        # 휴가 추가
        db_conn.execute("""
            INSERT INTO vacation (user_id, start_date, end_date, approved)
            VALUES ('user1', DATE('now'), DATE('now', '+7 days'), 1)
        """)
        db_conn.commit()

        repo = VacationRepository(db_conn)
        vacations = repo.get_active()

        assert len(vacations) >= 1


class TestWarningRepository:
    """WarningRepository 테스트"""

    def test_create_warning(self, db_conn):
        """경고 생성"""
        # 유저 생성
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        repo = WarningRepository(db_conn)

        warning_id = repo.create(
            user_id='user1',
            warning_type='activity',
            message='활동량 미달 경고'
        )

        assert warning_id > 0

    def test_get_by_user(self, db_conn):
        """유저별 경고 조회"""
        # 유저 생성
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        # 경고 추가
        db_conn.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES ('user1', 'activity', '테스트 경고')
        """)
        db_conn.commit()

        repo = WarningRepository(db_conn)
        warnings = repo.get_by_user('user1')

        assert len(warnings) >= 1
        assert warnings[0]['user_id'] == 'user1'


# ============================================================================
# 통합 테스트
# ============================================================================

class TestRepositoryIntegration:
    """Repository 통합 테스트"""

    def test_user_transaction_flow(self, db_conn):
        """유저-거래 흐름 테스트"""
        user_repo = UserRepository(db_conn)
        trans_repo = TransactionRepository(db_conn)

        # 1. 유저 생성
        user_id = user_repo.create('user1', 'testuser1', 'Test User 1')

        # 2. 거래 생성 (지급)
        trans_repo.create(user_id, 'reply', 100, '답글 보상')

        # 3. 유저 잔액 업데이트
        user_repo.update_balance(user_id, 100)

        # 4. 검증
        user = user_repo.get_by_id(user_id)
        assert user['balance'] == 100

        transactions = trans_repo.get_by_user(user_id)
        assert len(transactions) == 1
        assert transactions[0]['amount'] == 100

    def test_user_item_purchase_flow(self, db_conn):
        """유저-아이템 구매 흐름 테스트"""
        user_repo = UserRepository(db_conn)
        item_repo = ItemRepository(db_conn)
        trans_repo = TransactionRepository(db_conn)

        # 1. 유저 생성 (잔액 1000)
        user_id = user_repo.create('user1', 'testuser1', 'Test User 1')
        user_repo.update_balance(user_id, 1000)

        # 2. 아이템 생성
        item_id = item_repo.create('테스트 아이템', 500, '설명')

        # 3. 구매 거래 생성 (차감)
        trans_repo.create(user_id, 'purchase', -500, '아이템 구매', item_id=item_id)

        # 4. 유저 잔액 업데이트
        user_repo.update_balance(user_id, 500)

        # 5. 인벤토리 추가
        db_conn.execute("""
            INSERT INTO inventory (user_id, item_id, quantity)
            VALUES (?, ?, 1)
        """, (user_id, item_id))
        db_conn.commit()

        # 6. 검증
        user = user_repo.get_by_id(user_id)
        assert user['balance'] == 500

        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT * FROM inventory WHERE user_id = ? AND item_id = ?
        """, (user_id, item_id))
        inventory = cursor.fetchone()
        assert inventory is not None
        assert inventory['quantity'] == 1
