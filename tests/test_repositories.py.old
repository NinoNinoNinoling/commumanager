"""
Repository 레이어 테스트

UserRepository, TransactionRepository, ItemRepository 등을 테스트합니다.
Flask app context를 사용하여 static method를 테스트합니다.
"""
import pytest
from datetime import datetime, date, timedelta
from admin_web.models.user import User
from admin_web.models.transaction import Transaction
from admin_web.models.item import Item
from admin_web.models.vacation import Vacation
from admin_web.models.warning import Warning
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository
from admin_web.repositories.item_repository import ItemRepository
from admin_web.repositories.vacation_repository import VacationRepository
from admin_web.repositories.warning_repository import WarningRepository


class TestUserRepository:
    """UserRepository 테스트"""

    def test_find_all_users(self, app):
        """전체 유저 조회"""
        with app.app_context():
            # 샘플 유저 추가
            user = User(
                mastodon_id='test_find_all_user',
                username='testuser',
                display_name='Test User',
                role='user'
            )
            UserRepository.create(user)

            users, total = UserRepository.find_all()
            assert total >= 1
            assert any(u.username == 'testuser' for u in users)

    def test_find_user_by_id(self, app):
        """ID로 유저 조회"""
        with app.app_context():
            # 샘플 유저 추가
            user = User(
                mastodon_id='test_find_by_id_user',
                username='findbyid',
                display_name='Find By ID User',
                role='user'
            )
            UserRepository.create(user)

            found_user = UserRepository.find_by_id('test_find_by_id_user')
            assert found_user is not None
            assert found_user.username == 'findbyid'
            assert found_user.balance == 0

    def test_create_user(self, app):
        """유저 생성"""
        with app.app_context():
            new_user = User(
                mastodon_id='new_user_123',
                username='newuser',
                display_name='New User',
                role='user'
            )

            user = UserRepository.create(new_user)

            assert user.mastodon_id == 'new_user_123'
            assert user.username == 'newuser'
            assert user.balance == 0

    def test_update_user_balance(self, app):
        """유저 잔액 업데이트"""
        with app.app_context():
            # 유저 생성
            user = User(
                mastodon_id='balance_update_user',
                username='balanceuser',
                display_name='Balance User',
                role='user'
            )
            UserRepository.create(user)

            # 잔액 업데이트
            success = UserRepository.update_balance('balance_update_user', 2000)
            assert success

            # 확인
            updated_user = UserRepository.find_by_id('balance_update_user')
            assert updated_user.balance == 2000


class TestTransactionRepository:
    """TransactionRepository 테스트"""

    def test_create_transaction(self, app):
        """거래 내역 생성"""
        with app.app_context():
            # 유저 생성
            user = User(
                mastodon_id='transaction_user',
                username='transuser',
                display_name='Transaction User',
                role='user'
            )
            UserRepository.create(user)

            # 거래 생성
            transaction = Transaction(
                id=None,
                user_id='transaction_user',
                transaction_type='reply',
                amount=100,
                description='테스트 거래'
            )
            created_transaction = TransactionRepository.create(transaction)
            assert created_transaction.id > 0

    def test_find_by_user(self, app):
        """유저별 거래 내역 조회"""
        with app.app_context():
            # 유저 생성
            user = User(
                mastodon_id='trans_find_user',
                username='transfinduser',
                display_name='Transaction Find User',
                role='user'
            )
            UserRepository.create(user)

            # 거래 생성
            transaction = Transaction(
                id=None,
                user_id='trans_find_user',
                transaction_type='reply',
                amount=100,
                description='테스트 거래'
            )
            TransactionRepository.create(transaction)

            # 조회
            transactions, total = TransactionRepository.find_by_user('trans_find_user')
            assert total >= 1
            assert transactions[0].transaction_type == 'reply'


class TestItemRepository:
    """ItemRepository 테스트"""

    def test_find_all_items(self, app):
        """전체 아이템 조회"""
        with app.app_context():
            # 아이템 생성
            item = Item(
                id=None,
                name='테스트 아이템',
                description='찾기 테스트용',
                price=500,
                is_active=True
            )
            ItemRepository.create(item)

            # 조회
            items, total = ItemRepository.find_all()
            assert total >= 1

    def test_create_item(self, app):
        """아이템 생성"""
        with app.app_context():
            item = Item(
                id=None,
                name='새 아이템',
                description='생성 테스트용',
                price=300,
                is_active=True
            )
            created_item = ItemRepository.create(item)
            assert created_item.id > 0
            assert created_item.name == '새 아이템'
            assert created_item.price == 300

    def test_update_item(self, app):
        """아이템 업데이트"""
        with app.app_context():
            # 생성
            item = Item(
                id=None,
                name='업데이트 아이템',
                description='업데이트 테스트용',
                price=500,
                is_active=True
            )
            created_item = ItemRepository.create(item)

            # 업데이트
            created_item.price = 1000
            success = ItemRepository.update(created_item)
            assert success

            # 확인
            updated_item = ItemRepository.find_by_id(created_item.id)
            assert updated_item.price == 1000

    def test_delete_item(self, app):
        """아이템 삭제"""
        with app.app_context():
            # 생성
            item = Item(
                id=None,
                name='삭제 아이템',
                description='삭제 테스트용',
                price=500,
                is_active=True
            )
            created_item = ItemRepository.create(item)

            # 삭제
            success = ItemRepository.delete(created_item.id)
            assert success

            # 확인 (삭제되어야 함)
            deleted_item = ItemRepository.find_by_id(created_item.id)
            assert deleted_item is None


class TestVacationRepository:
    """VacationRepository 테스트"""

    def test_create_vacation(self, app):
        """휴가 생성"""
        with app.app_context():
            # 유저 생성
            user = User(
                mastodon_id='vacation_user',
                username='vacationuser',
                display_name='Vacation User',
                role='user'
            )
            UserRepository.create(user)

            # 휴가 생성
            vacation = Vacation(
                id=None,
                user_id='vacation_user',
                start_date='2024-01-01',
                end_date='2024-01-07',
                reason='테스트 휴가'
            )

            created = VacationRepository.create(vacation)
            assert created.user_id == 'vacation_user'

    def test_find_by_user(self, app):
        """유저별 휴가 조회"""
        with app.app_context():
            # 유저 생성
            user = User(
                mastodon_id='vacation_find_user',
                username='vacationfinduser',
                display_name='Vacation Find User',
                role='user'
            )
            UserRepository.create(user)

            # 휴가 생성
            vacation = Vacation(
                id=None,
                user_id='vacation_find_user',
                start_date='2024-01-01',
                end_date='2024-01-07',
                reason='테스트 휴가'
            )
            VacationRepository.create(vacation)

            # 조회
            vacations = VacationRepository.find_by_user('vacation_find_user')
            assert len(vacations) >= 1

    def test_count_active(self, app):
        """활성 휴가 카운트"""
        with app.app_context():
            # 유저 생성
            user = User(
                mastodon_id='active_vacation_user',
                username='activevacationuser',
                display_name='Active Vacation User',
                role='user'
            )
            UserRepository.create(user)

            # 현재 진행 중인 휴가 생성
            from admin_web.repositories.database import get_economy_db
            today = date.today()
            with get_economy_db() as conn:
                conn.execute("""
                    INSERT INTO vacation (user_id, start_date, end_date, reason, approved)
                    VALUES (?, ?, ?, ?, 1)
                """, ('active_vacation_user',
                      (today - timedelta(days=1)).isoformat(),
                      (today + timedelta(days=5)).isoformat(),
                      '테스트 휴가'))
                conn.commit()

            # 카운트
            count = VacationRepository.count_active()
            assert count >= 1


class TestWarningRepository:
    """WarningRepository 테스트"""

    def test_create_warning(self, app):
        """경고 생성"""
        with app.app_context():
            # 유저 생성
            user = User(
                mastodon_id='warning_user',
                username='warninguser',
                display_name='Warning User',
                role='user'
            )
            UserRepository.create(user)

            # 경고 생성
            warning = Warning(
                id=None,
                user_id='warning_user',
                warning_type='activity',
                message='활동량 부족'
            )

            created_warning = WarningRepository.create(warning)
            assert created_warning.id > 0

    def test_find_by_user(self, app):
        """유저별 경고 조회"""
        with app.app_context():
            # 유저 생성
            user = User(
                mastodon_id='warning_find_user',
                username='warningfinduser',
                display_name='Warning Find User',
                role='user'
            )
            UserRepository.create(user)

            # 경고 생성
            warning = Warning(
                id=None,
                user_id='warning_find_user',
                warning_type='activity',
                message='활동량 부족'
            )
            WarningRepository.create(warning)

            # 조회
            warnings, total = WarningRepository.find_by_user('warning_find_user')
            assert total >= 1
            assert warnings[0].warning_type == 'activity'


class TestRepositoryIntegration:
    """Repository 통합 테스트"""

    def test_user_transaction_flow(self, app):
        """유저 생성 → 거래 → 잔액 확인 흐름"""
        with app.app_context():
            # 1. 유저 생성
            user = User(
                mastodon_id='flow_test_user',
                username='flowuser',
                display_name='Flow User',
                role='user'
            )
            created_user = UserRepository.create(user)
            assert created_user.balance == 0

            # 2. 거래 생성 (수입)
            transaction = Transaction(
                id=None,
                user_id='flow_test_user',
                transaction_type='reply',
                amount=100,
                description='테스트 거래'
            )
            created_transaction = TransactionRepository.create(transaction)
            assert created_transaction.id > 0

            # 3. 잔액 업데이트 (실제로는 bot/database.py의 add_transaction이 자동으로 함)
            UserRepository.update_balance('flow_test_user', 100)

            # 4. 확인
            user = UserRepository.find_by_id('flow_test_user')
            assert user.balance == 100

            transactions, total = TransactionRepository.find_by_user('flow_test_user')
            assert total >= 1

    def test_user_item_purchase_flow(self, app):
        """유저 생성 → 잔액 설정 → 아이템 구매 흐름"""
        with app.app_context():
            # 1. 유저 생성
            user = User(
                mastodon_id='purchase_test_user',
                username='purchaseuser',
                display_name='Purchase User',
                role='user'
            )
            UserRepository.create(user)

            # 2. 잔액 설정
            UserRepository.update_balance('purchase_test_user', 1000)

            # 3. 아이템 생성
            item = Item(
                id=None,
                name='테스트 아이템',
                description='구매 테스트용',
                price=500,
                is_active=True
            )
            created_item = ItemRepository.create(item)

            # 4. 아이템 조회
            found_item = ItemRepository.find_by_id(created_item.id)
            assert found_item.price == 500

            # 5. 구매 거래 생성 (지출)
            transaction = Transaction(
                id=None,
                user_id='purchase_test_user',
                transaction_type='purchase',
                amount=-500,
                item_id=created_item.id,
                description=f"{found_item.name} 구매"
            )
            TransactionRepository.create(transaction)

            # 6. 잔액 차감
            UserRepository.update_balance('purchase_test_user', -500)

            # 7. 확인
            user = UserRepository.find_by_id('purchase_test_user')
            assert user.balance == 500

    def test_user_vacation_warning_flow(self, app):
        """유저 휴가 및 경고 흐름"""
        with app.app_context():
            # 1. 유저 생성
            user = User(
                mastodon_id='vacation_test_user',
                username='vacationuser',
                display_name='Vacation User',
                role='user'
            )
            UserRepository.create(user)

            # 2. 휴가 신청
            vacation = Vacation(
                id=None,
                user_id='vacation_test_user',
                start_date=(date.today() + timedelta(days=1)).isoformat(),
                end_date=(date.today() + timedelta(days=7)).isoformat(),
                reason='테스트 휴가'
            )
            VacationRepository.create(vacation)

            # 3. 경고 생성
            warning = Warning(
                id=None,
                user_id='vacation_test_user',
                warning_type='activity',
                message='활동량 부족 경고'
            )
            WarningRepository.create(warning)

            # 4. 확인
            vacations = VacationRepository.find_by_user('vacation_test_user')
            assert len(vacations) >= 1

            warnings = WarningRepository.find_by_user('vacation_test_user')
            assert len(warnings) >= 1
