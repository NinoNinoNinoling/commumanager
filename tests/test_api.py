"""
API 엔드포인트 테스트

Flask REST API를 테스트합니다.
"""
import pytest
import json


class TestUserAPI:
    """User API 테스트"""

    def test_get_all_users(self, auth_client, db_conn):
        """GET /api/users - 전체 유저 조회"""
        # 샘플 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, display_name, balance)
            VALUES ('user1', 'testuser1', 'Test User 1', 1000)
        """)
        db_conn.commit()

        response = auth_client.get('/api/users')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'users' in data
        assert len(data['users']) >= 1

    def test_get_user_detail(self, auth_client, db_conn):
        """GET /api/users/<user_id> - 유저 상세 조회"""
        # 샘플 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, display_name, balance)
            VALUES ('user1', 'testuser1', 'Test User 1', 1000)
        """)
        db_conn.commit()

        response = auth_client.get('/api/users/user1')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['user']['username'] == 'testuser1'
        assert data['user']['balance'] == 1000

    def test_adjust_balance(self, auth_client, db_conn):
        """POST /api/users/<user_id>/balance - 잔액 조정"""
        # 샘플 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, balance)
            VALUES ('user1', 'testuser1', 1000)
        """)
        db_conn.commit()

        response = auth_client.post(
            '/api/users/user1/balance',
            json={'amount': 500, 'reason': '테스트 지급'}
        )

        assert response.status_code == 200

        # 검증
        response = auth_client.get('/api/users/user1')
        data = json.loads(response.data)
        assert data['user']['balance'] == 1500


class TestItemAPI:
    """Item API 테스트"""

    def test_get_all_items(self, auth_client, db_conn):
        """GET /api/items - 전체 아이템 조회"""
        # 샘플 아이템 추가
        db_conn.execute("""
            INSERT INTO items (name, price, is_active)
            VALUES ('테스트 아이템', 500, 1)
        """)
        db_conn.commit()

        response = auth_client.get('/api/items')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'items' in data
        assert len(data['items']) >= 1

    def test_create_item(self, auth_client):
        """POST /api/items - 아이템 생성"""
        response = auth_client.post(
            '/api/items',
            json={
                'name': '새 아이템',
                'price': 1000,
                'description': '테스트 아이템',
                'category': '기타'
            }
        )

        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'item_id' in data
        assert data['item_id'] > 0

    def test_update_item(self, auth_client, db_conn):
        """PUT /api/items/<item_id> - 아이템 업데이트"""
        # 샘플 아이템 추가
        cursor = db_conn.cursor()
        cursor.execute("""
            INSERT INTO items (name, price)
            VALUES ('아이템1', 500)
        """)
        db_conn.commit()
        item_id = cursor.lastrowid

        response = auth_client.put(
            f'/api/items/{item_id}',
            json={'name': '수정된 아이템', 'price': 600}
        )

        assert response.status_code == 200

        # 검증
        response = auth_client.get(f'/api/items/{item_id}')
        data = json.loads(response.data)
        assert data['item']['name'] == '수정된 아이템'
        assert data['item']['price'] == 600

    def test_delete_item(self, auth_client, db_conn):
        """DELETE /api/items/<item_id> - 아이템 삭제"""
        # 샘플 아이템 추가
        cursor = db_conn.cursor()
        cursor.execute("""
            INSERT INTO items (name, price)
            VALUES ('아이템1', 500)
        """)
        db_conn.commit()
        item_id = cursor.lastrowid

        response = auth_client.delete(f'/api/items/{item_id}')
        assert response.status_code == 200

        # 검증 (비활성화됨)
        response = auth_client.get(f'/api/items/{item_id}')
        data = json.loads(response.data)
        assert data['item']['is_active'] == 0


class TestVacationAPI:
    """Vacation API 테스트"""

    def test_get_all_vacations(self, auth_client, db_conn):
        """GET /api/vacations - 전체 휴가 조회"""
        # 유저 및 휴가 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.execute("""
            INSERT INTO vacation (user_id, start_date, end_date, approved)
            VALUES ('user1', '2025-01-01', '2025-01-07', 1)
        """)
        db_conn.commit()

        response = auth_client.get('/api/vacations')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'vacations' in data
        assert len(data['vacations']) >= 1

    def test_create_vacation(self, auth_client, db_conn):
        """POST /api/vacations - 휴가 생성"""
        # 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        response = auth_client.post(
            '/api/vacations',
            json={
                'user_id': 'user1',
                'start_date': '2025-02-01',
                'end_date': '2025-02-07',
                'reason': '테스트 휴가'
            }
        )

        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'vacation_id' in data


class TestWarningAPI:
    """Warning API 테스트"""

    def test_get_all_warnings(self, auth_client, db_conn):
        """GET /api/warnings - 전체 경고 조회"""
        # 유저 및 경고 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.execute("""
            INSERT INTO warnings (user_id, warning_type, message)
            VALUES ('user1', 'activity', '테스트 경고')
        """)
        db_conn.commit()

        response = auth_client.get('/api/warnings')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'warnings' in data
        assert len(data['warnings']) >= 1

    def test_create_warning(self, auth_client, db_conn):
        """POST /api/warnings - 경고 생성"""
        # 유저 추가
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        response = auth_client.post(
            '/api/warnings',
            json={
                'user_id': 'user1',
                'warning_type': 'activity',
                'message': '활동량 미달 경고'
            }
        )

        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'warning_id' in data


class TestSettingsAPI:
    """Settings API 테스트"""

    def test_get_all_settings(self, auth_client):
        """GET /api/settings - 전체 설정 조회"""
        response = auth_client.get('/api/settings')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'settings' in data
        assert len(data['settings']) > 0

    def test_update_setting(self, auth_client):
        """PUT /api/settings/<key> - 설정 업데이트"""
        response = auth_client.put(
            '/api/settings/min_replies_48h',
            json={'value': '25'}
        )

        assert response.status_code == 200

        # 검증
        response = auth_client.get('/api/settings')
        data = json.loads(response.data)
        setting = next((s for s in data['settings'] if s['key'] == 'min_replies_48h'), None)
        assert setting is not None
        assert setting['value'] == '25'


# ============================================================================
# 인증 테스트
# ============================================================================

class TestAuthentication:
    """인증 테스트"""

    def test_unauthenticated_request(self, client):
        """인증 없이 API 요청 시 401"""
        response = client.get('/api/users')
        assert response.status_code in [401, 302]  # 리다이렉트 또는 Unauthorized

    def test_authenticated_request(self, auth_client):
        """인증된 요청은 성공"""
        response = auth_client.get('/api/settings')
        assert response.status_code == 200


# ============================================================================
# 에러 처리 테스트
# ============================================================================

class TestErrorHandling:
    """에러 처리 테스트"""

    def test_get_nonexistent_user(self, auth_client):
        """존재하지 않는 유저 조회 시 404"""
        response = auth_client.get('/api/users/nonexistent_user')
        assert response.status_code == 404

    def test_get_nonexistent_item(self, auth_client):
        """존재하지 않는 아이템 조회 시 404"""
        response = auth_client.get('/api/items/99999')
        assert response.status_code == 404

    def test_invalid_json(self, auth_client):
        """잘못된 JSON 형식 시 400"""
        response = auth_client.post(
            '/api/items',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_missing_required_field(self, auth_client):
        """필수 필드 누락 시 400"""
        response = auth_client.post(
            '/api/items',
            json={'name': '아이템'}  # price 누락
        )
        assert response.status_code == 400


# ============================================================================
# 통합 테스트
# ============================================================================

class TestAPIIntegration:
    """API 통합 테스트"""

    def test_user_item_purchase_flow(self, auth_client, db_conn):
        """유저-아이템 구매 API 흐름 테스트"""
        # 1. 유저 생성
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username, balance)
            VALUES ('user1', 'testuser1', 1000)
        """)
        db_conn.commit()

        # 2. 아이템 생성
        response = auth_client.post(
            '/api/items',
            json={'name': '테스트 아이템', 'price': 500}
        )
        item_id = json.loads(response.data)['item_id']

        # 3. 잔액 조회
        response = auth_client.get('/api/users/user1')
        assert json.loads(response.data)['user']['balance'] == 1000

        # 4. 구매 (잔액 차감)
        response = auth_client.post(
            '/api/users/user1/balance',
            json={'amount': -500, 'reason': '아이템 구매'}
        )
        assert response.status_code == 200

        # 5. 검증
        response = auth_client.get('/api/users/user1')
        assert json.loads(response.data)['user']['balance'] == 500

    def test_vacation_management_flow(self, auth_client, db_conn):
        """휴가 관리 API 흐름 테스트"""
        # 1. 유저 생성
        db_conn.execute("""
            INSERT INTO users (mastodon_id, username) VALUES ('user1', 'testuser1')
        """)
        db_conn.commit()

        # 2. 휴가 생성
        response = auth_client.post(
            '/api/vacations',
            json={
                'user_id': 'user1',
                'start_date': '2025-03-01',
                'end_date': '2025-03-07',
                'reason': '개인 사유'
            }
        )
        assert response.status_code == 201
        vacation_id = json.loads(response.data)['vacation_id']

        # 3. 휴가 목록 조회
        response = auth_client.get('/api/vacations')
        vacations = json.loads(response.data)['vacations']
        assert len(vacations) >= 1

        # 4. 휴가 승인
        response = auth_client.put(
            f'/api/vacations/{vacation_id}',
            json={'approved': True}
        )
        assert response.status_code == 200
