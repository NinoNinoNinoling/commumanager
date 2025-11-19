"""
Repository 레이어 테스트

UserRepository, TransactionRepository, ItemRepository 등을 테스트합니다.
Flask app context를 사용하여 static method를 테스트합니다.
"""
import pytest
from datetime import datetime, date, timedelta
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.transaction_repository import TransactionRepository
from admin_web.repositories.item_repository import ItemRepository
from admin_web.repositories.vacation_repository import VacationRepository
from admin_web.repositories.warning_repository import WarningRepository


class TestUserRepository:
    """UserRepository 테스트"""

    def test_find_all_users(self, app, sample_user_data):
        """전체 유저 조회"""
        with app.app_context():
            # 샘플 유저 추가
            from admin_web.repositories.database import get_economy_db
            with get_economy_db() as conn:
                conn.execute("""
                    INSERT INTO users (mastodon_id, username, display_name, balance)
                    VALUES (?, ?, ?, ?)
                """, (sample_user_data['mastodon_id'], sample_user_data['username'],
                      sample_user_data['display_name'], sample_user_data['balance']))
                conn.commit()

            users, total = UserRepository.find_all()
            assert total >= 1
            assert any(u['username'] == sample_user_data['username'] for u in users)

    def test_find_user_by_id(self, app, sample_user_data):
        """ID로 유저 조회"""
        with app.app_context():
            # 샘플 유저 추가
            from admin_web.repositories.database import get_economy_db
            with get_economy_db() as conn:
                conn.execute("""
                    INSERT INTO users (mastodon_id, username, display_name, balance)
                    VALUES (?, ?, ?, ?)
                """, (sample_user_data['mastodon_id'], sample_user_data['username'],
                      sample_user_data['display_name'], sample_user_data['balance']))
                conn.commit()

            user = UserRepository.find_by_id(sample_user_data['mastodon_id'])
            assert user is not None
            assert user['username'] == sample_user_data['username']
            assert user['balance'] == sample_user_data['balance']

    def test_create_user(self, app):
        """유저 생성"""
        with app.app_context():
            from admin_web.models.user import User

            new_user = User(
                mastodon_id='new_user_123',
                username='newuser',
                display_name='New User',
                role='user'
            )

            user = UserRepository.create(new_user)

            assert user['mastodon_id'] == 'new_user_123'
            assert user['username'] == 'newuser'
            assert user['balance'] == 0

    def test_update_user_balance(self, app, sample_user_data):
        """유저 잔액 업데이트"""
        with app.app_context():
            # 유저 생성
            UserRepository.create(sample_user_data)

            # 잔액 업데이트
            success = UserRepository.update_balance(sample_user_data['mastodon_id'], 2000)
            assert success

            # 확인
            user = UserRepository.find_by_id(sample_user_data['mastodon_id'])
            assert user['balance'] == 2000


class TestTransactionRepository:
    """TransactionRepository 테스트"""

    def test_create_transaction(self, app, sample_user_data, sample_transaction_data):
        """거래 내역 생성"""
        with app.app_context():
            # 유저 생성
            UserRepository.create(sample_user_data)

            # 거래 생성
            transaction_id = TransactionRepository.create(sample_transaction_data)
            assert transaction_id > 0

    def test_find_by_user(self, app, sample_user_data, sample_transaction_data):
        """유저별 거래 내역 조회"""
        with app.app_context():
            # 유저 생성
            UserRepository.create(sample_user_data)

            # 거래 생성
            TransactionRepository.create(sample_transaction_data)

            # 조회
            transactions, total = TransactionRepository.find_by_user(sample_user_data['mastodon_id'])
            assert total >= 1
            assert transactions[0]['transaction_type'] == 'reply'


class TestItemRepository:
    """ItemRepository 테스트"""

    def test_find_all_items(self, app, sample_item_data):
        """전체 아이템 조회"""
        with app.app_context():
            # 아이템 생성
            ItemRepository.create(sample_item_data)

            # 조회
            items, total = ItemRepository.find_all()
            assert total >= 1

    def test_create_item(self, app, sample_item_data):
        """아이템 생성"""
        with app.app_context():
            item_id = ItemRepository.create(sample_item_data)
            assert item_id > 0

            item = ItemRepository.find_by_id(item_id)
            assert item['name'] == sample_item_data['name']
            assert item['price'] == sample_item_data['price']

    def test_update_item(self, app, sample_item_data):
        """아이템 업데이트"""
        with app.app_context():
            # 생성
            item_id = ItemRepository.create(sample_item_data)

            # 업데이트
            updated_data = sample_item_data.copy()
            updated_data['price'] = 1000

            success = ItemRepository.update(item_id, updated_data)
            assert success

            # 확인
            item = ItemRepository.find_by_id(item_id)
            assert item['price'] == 1000

    def test_delete_item(self, app, sample_item_data):
        """아이템 삭제"""
        with app.app_context():
            # 생성
            item_id = ItemRepository.create(sample_item_data)

            # 삭제
            success = ItemRepository.delete(item_id)
            assert success

            # 확인 (is_active가 0이 됨)
            item = ItemRepository.find_by_id(item_id)
            assert item is None or item['is_active'] == 0


class TestVacationRepository:
    """VacationRepository 테스트"""

    def test_create_vacation(self, app, sample_user_data):
        """휴가 생성"""
        with app.app_context():
            # 유저 생성
            UserRepository.create(sample_user_data)

            # 휴가 생성
            from admin_web.models.vacation import Vacation
            vacation = Vacation(
                user_id=sample_user_data['mastodon_id'],
                start_date='2024-01-01',
                end_date='2024-01-07',
                reason='테스트 휴가'
            )

            created = VacationRepository.create(vacation)
            assert created.user_id == sample_user_data['mastodon_id']

    def test_find_by_user(self, app, sample_user_data):
        """유저별 휴가 조회"""
        with app.app_context():
            # 유저 생성
            UserRepository.create(sample_user_data)

            # 휴가 생성
            from admin_web.models.vacation import Vacation
            vacation = Vacation(
                user_id=sample_user_data['mastodon_id'],
                start_date='2024-01-01',
                end_date='2024-01-07',
                reason='테스트 휴가'
            )
            VacationRepository.create(vacation)

            # 조회
            vacations = VacationRepository.find_by_user(sample_user_data['mastodon_id'])
            assert len(vacations) >= 1

    def test_count_active(self, app, sample_user_data):
        """활성 휴가 카운트"""
        with app.app_context():
            # 유저 생성
            UserRepository.create(sample_user_data)

            # 현재 진행 중인 휴가 생성
            from admin_web.repositories.database import get_economy_db
            today = date.today()
            with get_economy_db() as conn:
                conn.execute("""
                    INSERT INTO vacation (user_id, start_date, end_date, reason, approved)
                    VALUES (?, ?, ?, ?, 1)
                """, (sample_user_data['mastodon_id'],
                      (today - timedelta(days=1)).isoformat(),
                      (today + timedelta(days=5)).isoformat(),
                      '테스트 휴가'))
                conn.commit()

            # 카운트
            count = VacationRepository.count_active()
            assert count >= 1


class TestWarningRepository:
    """WarningRepository 테스트"""

    def test_create_warning(self, app, sample_user_data):
        """경고 생성"""
        with app.app_context():
            # 유저 생성
            UserRepository.create(sample_user_data)

            # 경고 생성
            warning_data = {
                'user_id': sample_user_data['mastodon_id'],
                'warning_type': 'activity',
                'message': '활동량 부족',
                'dm_sent': 0
            }

            warning_id = WarningRepository.create(warning_data)
            assert warning_id > 0

    def test_find_by_user(self, app, sample_user_data):
        """유저별 경고 조회"""
        with app.app_context():
            # 유저 생성
            UserRepository.create(sample_user_data)

            # 경고 생성
            warning_data = {
                'user_id': sample_user_data['mastodon_id'],
                'warning_type': 'activity',
                'message': '활동량 부족',
                'dm_sent': 0
            }
            WarningRepository.create(warning_data)

            # 조회
            warnings = WarningRepository.find_by_user(sample_user_data['mastodon_id'])
            assert len(warnings) >= 1
            assert warnings[0]['warning_type'] == 'activity'


class TestRepositoryIntegration:
    """Repository 통합 테스트"""

    def test_user_transaction_flow(self, app):
        """유저 생성 → 거래 → 잔액 확인 흐름"""
        with app.app_context():
            # 1. 유저 생성
            user_data = {
                'mastodon_id': 'flow_test_user',
                'username': 'flowuser',
                'display_name': 'Flow User',
                'role': 'user'
            }
            user = UserRepository.create(user_data)
            assert user['balance'] == 0

            # 2. 거래 생성 (수입)
            transaction_data = {
                'user_id': 'flow_test_user',
                'transaction_type': 'reply',
                'amount': 100,
                'description': '테스트 거래'
            }
            transaction_id = TransactionRepository.create(transaction_data)
            assert transaction_id > 0

            # 3. 잔액 업데이트 (실제로는 bot/database.py의 add_transaction이 자동으로 함)
            UserRepository.update_balance('flow_test_user', 100)

            # 4. 확인
            user = UserRepository.find_by_id('flow_test_user')
            assert user['balance'] == 100

            transactions, total = TransactionRepository.find_by_user('flow_test_user')
            assert total >= 1

    def test_user_item_purchase_flow(self, app):
        """유저 생성 → 잔액 설정 → 아이템 구매 흐름"""
        with app.app_context():
            # 1. 유저 생성
            user_data = {
                'mastodon_id': 'purchase_test_user',
                'username': 'purchaseuser',
                'display_name': 'Purchase User',
                'role': 'user'
            }
            UserRepository.create(user_data)

            # 2. 잔액 설정
            UserRepository.update_balance('purchase_test_user', 1000)

            # 3. 아이템 생성
            item_data = {
                'name': '테스트 아이템',
                'description': '구매 테스트용',
                'price': 500,
                'category': '기타',
                'is_active': True
            }
            item_id = ItemRepository.create(item_data)

            # 4. 아이템 조회
            item = ItemRepository.find_by_id(item_id)
            assert item['price'] == 500

            # 5. 구매 거래 생성 (지출)
            transaction_data = {
                'user_id': 'purchase_test_user',
                'transaction_type': 'purchase',
                'amount': -500,
                'item_id': item_id,
                'description': f"{item['name']} 구매"
            }
            TransactionRepository.create(transaction_data)

            # 6. 잔액 차감
            UserRepository.update_balance('purchase_test_user', 500)

            # 7. 확인
            user = UserRepository.find_by_id('purchase_test_user')
            assert user['balance'] == 500

    def test_user_vacation_warning_flow(self, app):
        """유저 휴가 및 경고 흐름"""
        with app.app_context():
            # 1. 유저 생성
            user_data = {
                'mastodon_id': 'vacation_test_user',
                'username': 'vacationuser',
                'display_name': 'Vacation User',
                'role': 'user'
            }
            UserRepository.create(user_data)

            # 2. 휴가 신청
            from admin_web.models.vacation import Vacation
            vacation = Vacation(
                user_id='vacation_test_user',
                start_date=(date.today() + timedelta(days=1)).isoformat(),
                end_date=(date.today() + timedelta(days=7)).isoformat(),
                reason='테스트 휴가'
            )
            VacationRepository.create(vacation)

            # 3. 경고 생성
            warning_data = {
                'user_id': 'vacation_test_user',
                'warning_type': 'activity',
                'message': '활동량 부족 경고',
                'dm_sent': 0
            }
            WarningRepository.create(warning_data)

            # 4. 확인
            vacations = VacationRepository.find_by_user('vacation_test_user')
            assert len(vacations) >= 1

            warnings = WarningRepository.find_by_user('vacation_test_user')
            assert len(warnings) >= 1
