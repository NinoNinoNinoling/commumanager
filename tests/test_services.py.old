"""
Service 레이어 테스트

UserService, DashboardService, ItemService 등을 테스트합니다.
Flask app context를 사용하여 Service를 테스트합니다.
"""
import pytest
from admin_web.models.user import User
from admin_web.models.item import Item
from admin_web.models.vacation import Vacation
from admin_web.models.warning import Warning
from admin_web.repositories.user_repository import UserRepository
from admin_web.repositories.item_repository import ItemRepository
from admin_web.repositories.vacation_repository import VacationRepository
from admin_web.repositories.warning_repository import WarningRepository
from admin_web.services.user_service import UserService
from admin_web.services.dashboard_service import DashboardService
from admin_web.services.item_service import ItemService
from admin_web.services.vacation_service import VacationService
from admin_web.services.warning_service import WarningService


class TestUserService:
    """UserService 테스트"""

    def test_get_users(self, app):
        """유저 목록 조회"""
        with app.app_context():
            # 테스트 유저 생성
            user = User(
                mastodon_id='service_test_user',
                username='serviceuser',
                display_name='Service Test User',
                role='user'
            )
            UserRepository.create(user)

            # Service 테스트
            service = UserService()
            result = service.get_users()

            assert 'users' in result
            assert 'pagination' in result
            assert result['pagination']['total'] >= 1

    def test_get_user(self, app):
        """유저 상세 조회"""
        with app.app_context():
            # 테스트 유저 생성
            user = User(
                mastodon_id='detail_test_user',
                username='detailuser',
                display_name='Detail Test User',
                role='user'
            )
            UserRepository.create(user)

            # Service 테스트
            service = UserService()
            user = service.get_user('detail_test_user')

            assert user is not None
            assert user.username == 'detailuser'

    def test_adjust_balance(self, app):
        """잔액 조정"""
        with app.app_context():
            # 테스트 유저 생성
            user = User(
                mastodon_id='balance_test_user',
                username='balanceuser',
                display_name='Balance Test User',
                role='user'
            )
            UserRepository.create(user)

            # Service 테스트
            service = UserService()
            success = service.adjust_balance('balance_test_user', 500, 'admin', '테스트 지급')

            assert success
            updated_user = UserRepository.find_by_id('balance_test_user')
            assert updated_user.balance == 500


class TestDashboardService:
    """DashboardService 테스트"""

    def test_get_stats(self, app):
        """대시보드 통계 조회"""
        with app.app_context():
            # 테스트 데이터 생성
            user = User(
                mastodon_id='stats_test_user',
                username='statsuser',
                display_name='Stats Test User',
                role='user'
            )
            UserRepository.create(user)

            # Service 테스트
            service = DashboardService()
            stats = service.get_stats()

            assert 'users' in stats
            assert 'currency' in stats
            assert stats['users']['total'] >= 1


class TestItemService:
    """ItemService 테스트"""

    def test_get_items(self, app):
        """아이템 목록 조회"""
        with app.app_context():
            # 테스트 아이템 생성
            item = Item(
                id=None,
                name='서비스 테스트 아이템',
                description='Service test',
                price=1000,
                is_active=True
            )
            ItemRepository.create(item)

            # Service 테스트
            service = ItemService()
            result = service.get_items()

            assert 'items' in result
            assert 'pagination' in result
            assert result['pagination']['total'] >= 1

    def test_create_item(self, app):
        """아이템 생성"""
        with app.app_context():
            service = ItemService()

            item_data = {
                'name': '새 아이템',
                'description': '서비스로 생성',
                'price': 2000,
                'category': 'test',
                'is_active': True
            }

            created_item = service.create_item(item_data)

            assert created_item.id is not None
            assert created_item.name == '새 아이템'
            assert created_item.price == 2000

    def test_update_item(self, app):
        """아이템 업데이트"""
        with app.app_context():
            # 아이템 생성
            item = Item(
                id=None,
                name='업데이트 테스트',
                description='Update test',
                price=1000,
                is_active=True
            )
            created_item = ItemRepository.create(item)

            # Service로 업데이트
            service = ItemService()
            update_data = {
                'name': '업데이트됨',
                'price': 1500
            }

            success = service.update_item(created_item.id, update_data)

            assert success
            updated_item = ItemRepository.find_by_id(created_item.id)
            assert updated_item.price == 1500

    def test_delete_item(self, app):
        """아이템 삭제"""
        with app.app_context():
            # 아이템 생성
            item = Item(
                id=None,
                name='삭제 테스트',
                description='Delete test',
                price=1000,
                is_active=True
            )
            created_item = ItemRepository.create(item)

            # Service로 삭제
            service = ItemService()
            success = service.delete_item(created_item.id)

            assert success
            deleted_item = ItemRepository.find_by_id(created_item.id)
            assert deleted_item is None


class TestVacationService:
    """VacationService 테스트"""

    def test_get_vacations(self, app):
        """휴가 목록 조회"""
        with app.app_context():
            # 테스트 유저 및 휴가 생성
            user = User(
                mastodon_id='vacation_service_user',
                username='vacationserviceuser',
                display_name='Vacation Service User',
                role='user'
            )
            UserRepository.create(user)

            vacation = Vacation(
                id=None,
                user_id='vacation_service_user',
                start_date='2024-01-01',
                end_date='2024-01-07',
                reason='서비스 테스트 휴가'
            )
            VacationRepository.create(vacation)

            # Service 테스트
            service = VacationService()
            result = service.get_vacations()

            assert 'vacations' in result
            assert 'pagination' in result
            assert result['pagination']['total'] >= 1

    def test_create_vacation(self, app):
        """휴가 생성"""
        with app.app_context():
            # 테스트 유저 생성
            user = User(
                mastodon_id='vacation_create_user',
                username='vacationcreateuser',
                display_name='Vacation Create User',
                role='user'
            )
            UserRepository.create(user)

            # Service로 휴가 생성
            service = VacationService()
            vacation_data = {
                'user_id': 'vacation_create_user',
                'start_date': '2024-02-01',
                'end_date': '2024-02-07',
                'reason': '서비스로 생성한 휴가'
            }

            created_vacation = service.create_vacation(vacation_data)

            assert created_vacation.user_id == 'vacation_create_user'


class TestWarningService:
    """WarningService 테스트"""

    def test_get_warnings(self, app):
        """경고 목록 조회"""
        with app.app_context():
            # 테스트 유저 및 경고 생성
            user = User(
                mastodon_id='warning_service_user',
                username='warningserviceuser',
                display_name='Warning Service User',
                role='user'
            )
            UserRepository.create(user)

            warning = Warning(
                id=None,
                user_id='warning_service_user',
                warning_type='activity',
                message='서비스 테스트 경고'
            )
            WarningRepository.create(warning)

            # Service 테스트
            service = WarningService()
            result = service.get_warnings()

            assert 'warnings' in result
            assert 'pagination' in result
            assert result['pagination']['total'] >= 1

    def test_create_warning(self, app):
        """경고 생성"""
        with app.app_context():
            # 테스트 유저 생성
            user = User(
                mastodon_id='warning_create_user',
                username='warningcreateuser',
                display_name='Warning Create User',
                role='user'
            )
            UserRepository.create(user)

            # Service로 경고 생성
            service = WarningService()
            warning_data = {
                'user_id': 'warning_create_user',
                'warning_type': 'manual',
                'message': '서비스로 생성한 경고',
                'admin_name': 'admin'
            }

            created_warning = service.create_warning(warning_data)

            assert created_warning.user_id == 'warning_create_user'

    def test_get_user_warnings(self, app):
        """유저별 경고 조회"""
        with app.app_context():
            # 테스트 유저 및 경고 생성
            user = User(
                mastodon_id='user_warning_test',
                username='userwarningtest',
                display_name='User Warning Test',
                role='user'
            )
            UserRepository.create(user)

            warning = Warning(
                id=None,
                user_id='user_warning_test',
                warning_type='activity',
                message='유저 경고 테스트'
            )
            WarningRepository.create(warning)

            # Service 테스트
            service = WarningService()
            result = service.get_user_warnings('user_warning_test')

            assert 'warnings' in result
            assert len(result['warnings']) >= 1


class TestServiceIntegration:
    """Service 통합 테스트"""

    def test_user_item_flow(self, app):
        """유저 생성 → 잔액 조정 → 아이템 구매 흐름"""
        with app.app_context():
            # 1. 유저 생성
            user = User(
                mastodon_id='integration_user',
                username='integrationuser',
                display_name='Integration User',
                role='user'
            )
            UserRepository.create(user)

            # 2. 잔액 지급
            user_service = UserService()
            user_service.adjust_balance('integration_user', 2000, 'admin', '초기 지급')

            # 3. 아이템 생성
            item_service = ItemService()
            item_data = {
                'name': '통합 테스트 아이템',
                'price': 500,
                'is_active': True
            }
            created_item = item_service.create_item(item_data)

            # 4. 확인
            user = UserRepository.find_by_id('integration_user')
            assert user.balance == 2000

            item = ItemRepository.find_by_id(created_item.id)
            assert item.price == 500

    def test_dashboard_stats(self, app):
        """대시보드 통계 계산"""
        with app.app_context():
            # 여러 유저 생성
            for i in range(3):
                user = User(
                    mastodon_id=f'stats_user_{i}',
                    username=f'statsuser{i}',
                    display_name=f'Stats User {i}',
                    role='user'
                )
                UserRepository.create(user)

            # 통계 조회
            dashboard_service = DashboardService()
            stats = dashboard_service.get_stats()

            assert stats['users']['total'] >= 3

    def test_vacation_warning_flow(self, app):
        """휴가 신청 및 경고 발생 흐름"""
        with app.app_context():
            # 1. 유저 생성
            user = User(
                mastodon_id='flow_user',
                username='flowuser',
                display_name='Flow User',
                role='user'
            )
            UserRepository.create(user)

            # 2. 휴가 신청
            vacation_service = VacationService()
            vacation_data = {
                'user_id': 'flow_user',
                'start_date': '2024-03-01',
                'end_date': '2024-03-07',
                'reason': '개인 사정'
            }
            vacation = vacation_service.create_vacation(vacation_data)

            # 3. 경고 발생
            warning_service = WarningService()
            warning_data = {
                'user_id': 'flow_user',
                'warning_type': 'activity',
                'message': '활동 부족',
                'admin_name': 'system'
            }
            warning = warning_service.create_warning(warning_data)

            # 4. 확인
            assert vacation.user_id == 'flow_user'
            assert warning.user_id == 'flow_user'
