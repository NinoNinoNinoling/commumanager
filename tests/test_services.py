"""
Service 레이어 테스트

UserService, DashboardService, ItemService 등을 테스트합니다.
"""
import pytest
from admin_web.services.user_service import UserService
from admin_web.services.dashboard_service import DashboardService
from admin_web.services.item_service import ItemService
from admin_web.services.vacation_service import VacationService
from admin_web.services.warning_service import WarningService


class TestUserService:
    """UserService 테스트"""

    def test_get_all_users(self, db_conn):
        """전체 유저 조회"""
        service = UserService(db_conn)

        # 샘플 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, display_name, balance)
            VALUES ('user1', 'testuser1', 'Test User 1', 1000)
        """)
        db_conn.commit()

        users = service.get_all_users()
        assert len(users) >= 1
        assert any(u['username'] == 'testuser1' for u in users)

    def test_get_user_detail(self, db_conn):
        """유저 상세 조회"""
        service = UserService(db_conn)

        # 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, display_name, balance)
            VALUES ('user1', 'testuser1', 'Test User 1', 1000)
        """)
        db_conn.commit()

        detail = service.get_user_detail('user1')
        assert detail is not None
        assert detail['user']['username'] == 'testuser1'
        assert detail['user']['balance'] == 1000
        assert 'transactions' in detail
        assert 'warnings' in detail

    def test_adjust_balance(self, db_conn):
        """잔액 조정"""
        service = UserService(db_conn)

        # 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, balance)
            VALUES ('user1', 'testuser1', 1000)
        """)
        db_conn.commit()

        # 잔액 조정 (+500)
        success = service.adjust_balance(
            user_id='user1',
            amount=500,
            reason='테스트 지급',
            admin_name='admin'
        )

        assert success is True

        # 검증
        detail = service.get_user_detail('user1')
        assert detail['user']['balance'] == 1500

        # 거래 내역 확인
        assert len(detail['transactions']) >= 1
        assert detail['transactions'][0]['amount'] == 500


class TestDashboardService:
    """DashboardService 테스트"""

    def test_get_stats(self, db_conn):
        """대시보드 통계 조회"""
        service = DashboardService(db_conn)

        # 샘플 데이터 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, balance)
            VALUES ('user1', 'testuser1', 1000), ('user2', 'testuser2', 2000)
        """)
        db_conn.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount)
            VALUES ('user1', 'reply', 100), ('user2', 'reply', 200)
        """)
        db_conn.commit()

        stats = service.get_stats()

        assert stats is not None
        assert 'total_users' in stats
        assert 'total_balance' in stats
        assert 'total_transactions' in stats
        assert stats['total_users'] >= 2
        assert stats['total_balance'] >= 3000

    def test_get_recent_activity(self, db_conn):
        """최근 활동 조회"""
        service = DashboardService(db_conn)

        # 샘플 데이터 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username)
            VALUES ('user1', 'testuser1')
        """)
        db_conn.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount)
            VALUES ('user1', 'reply', 100)
        """)
        db_conn.commit()

        activity = service.get_recent_activity()

        assert activity is not None
        assert 'recent_transactions' in activity
        assert len(activity['recent_transactions']) >= 1


class TestItemService:
    """ItemService 테스트"""

    def test_get_all_items(self, db_conn):
        """전체 아이템 조회"""
        service = ItemService(db_conn)

        # 샘플 아이템 추가
        db_conn.execute("""
            INSERT INTO items (name, price, is_active)
            VALUES ('테스트 아이템', 500, 1)
        """)
        db_conn.commit()

        items = service.get_all_items()
        assert len(items) >= 1

    def test_create_item(self, db_conn):
        """아이템 생성"""
        service = ItemService(db_conn)

        item_id = service.create_item(
            name='새 아이템',
            price=1000,
            description='테스트 아이템',
            category='기타',
            created_by='admin'
        )

        assert item_id > 0

        # 검증
        item = service.get_item_detail(item_id)
        assert item['name'] == '새 아이템'

    def test_update_item(self, db_conn):
        """아이템 업데이트"""
        service = ItemService(db_conn)

        # 아이템 생성
        item_id = service.create_item('아이템1', 500, created_by='admin')

        # 업데이트
        success = service.update_item(
            item_id=item_id,
            name='수정된 아이템',
            price=600
        )

        assert success is True

        # 검증
        item = service.get_item_detail(item_id)
        assert item['name'] == '수정된 아이템'
        assert item['price'] == 600

    def test_delete_item(self, db_conn):
        """아이템 삭제"""
        service = ItemService(db_conn)

        # 아이템 생성
        item_id = service.create_item('아이템1', 500, created_by='admin')

        # 삭제
        success = service.delete_item(item_id)
        assert success is True

        # 검증
        item = service.get_item_detail(item_id)
        assert item['is_active'] == 0


class TestVacationService:
    """VacationService 테스트"""

    def test_get_all_vacations(self, db_conn):
        """전체 휴가 조회"""
        service = VacationService(db_conn)

        # 유저 및 휴가 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.execute("""
            INSERT INTO vacation (user_id, start_date, end_date, approved)
            VALUES ('user1', '2025-01-01', '2025-01-07', 1)
        """)
        db_conn.commit()

        vacations = service.get_all_vacations()
        assert len(vacations) >= 1

    def test_create_vacation(self, db_conn):
        """휴가 생성"""
        service = VacationService(db_conn)

        # 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        vacation_id = service.create_vacation(
            user_id='user1',
            start_date='2025-02-01',
            end_date='2025-02-07',
            reason='테스트 휴가',
            registered_by='admin'
        )

        assert vacation_id > 0

    def test_approve_vacation(self, db_conn):
        """휴가 승인"""
        service = VacationService(db_conn)

        # 유저 및 휴가 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.execute("""
            INSERT INTO vacation (user_id, start_date, end_date, approved)
            VALUES ('user1', '2025-01-01', '2025-01-07', 0)
        """)
        db_conn.commit()

        cursor = db_conn.cursor()
        cursor.execute("SELECT id FROM vacation WHERE user_id = 'user1'")
        vacation_id = cursor.fetchone()['id']

        # 승인
        success = service.approve_vacation(vacation_id, True)
        assert success is True


class TestWarningService:
    """WarningService 테스트"""

    def test_get_all_warnings(self, db_conn):
        """전체 경고 조회"""
        service = WarningService(db_conn)

        # 유저 및 경고 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES ('user1', 'activity', '테스트 경고')
        """)
        db_conn.commit()

        warnings = service.get_all_warnings()
        assert len(warnings) >= 1

    def test_create_warning(self, db_conn):
        """경고 생성"""
        service = WarningService(db_conn)

        # 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        warning_id = service.create_warning(
            user_id='user1',
            warning_type='activity',
            message='활동량 미달 경고',
            admin_name='admin'
        )

        assert warning_id > 0

    def test_get_user_warnings(self, db_conn):
        """유저별 경고 조회"""
        service = WarningService(db_conn)

        # 유저 및 경고 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES ('user1', 'activity', '경고1'), ('user1', 'activity', '경고2')
        """)
        db_conn.commit()

        warnings = service.get_user_warnings('user1')
        assert len(warnings) >= 2


# ============================================================================
# 통합 테스트
# ============================================================================

class TestServiceIntegration:
    """Service 통합 테스트"""

    def test_user_balance_adjustment_flow(self, db_conn):
        """유저 잔액 조정 흐름 테스트"""
        user_service = UserService(db_conn)

        # 1. 유저 생성
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, balance)
            VALUES ('user1', 'testuser1', 1000)
        """)
        db_conn.commit()

        # 2. 잔액 조정
        user_service.adjust_balance('user1', 500, '테스트 지급', 'admin')

        # 3. 검증
        detail = user_service.get_user_detail('user1')
        assert detail['user']['balance'] == 1500
        assert len(detail['transactions']) >= 1

    def test_dashboard_stats_calculation(self, db_conn):
        """대시보드 통계 계산 테스트"""
        dashboard_service = DashboardService(db_conn)

        # 샘플 데이터
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, balance)
            VALUES ('user1', 'testuser1', 1000), ('user2', 'testuser2', 2000)
        """)
        db_conn.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount)
            VALUES ('user1', 'reply', 100), ('user2', 'attendance', 50)
        """)
        db_conn.commit()

        # 통계 조회
        stats = dashboard_service.get_stats()

        # 검증
        assert stats['total_users'] >= 2
        assert stats['total_balance'] >= 3000
        assert stats['total_transactions'] >= 2

    def test_vacation_management_flow(self, db_conn):
        """휴가 관리 흐름 테스트"""
        vacation_service = VacationService(db_conn)

        # 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        # 1. 휴가 생성
        vacation_id = vacation_service.create_vacation(
            user_id='user1',
            start_date='2025-03-01',
            end_date='2025-03-07',
            reason='개인 사유',
            registered_by='self'
        )

        # 2. 휴가 목록 조회
        vacations = vacation_service.get_all_vacations()
        assert len(vacations) >= 1

        # 3. 휴가 승인
        success = vacation_service.approve_vacation(vacation_id, True)
        assert success is True
