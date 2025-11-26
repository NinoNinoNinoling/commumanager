"""
User API E2E tests
"""
import json
import pytest
import sqlite3

@pytest.fixture
def temp_db_with_users(temp_db):
    """Fixture to create a temporary database with multiple users."""
    from init_db import initialize_database
    initialize_database(temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (mastodon_id, username, display_name, role) VALUES (?, ?, ?, ?)", 
                   ('12345', 'testuser1', 'Test User One', 'user'))
    cursor.execute("INSERT INTO users (mastodon_id, username, display_name, role) VALUES (?, ?, ?, ?)", 
                   ('67890', 'testuser2', 'Test User Two', 'admin'))
    conn.commit()
    conn.close()
    return temp_db

def test_get_users_returns_200_and_user_list(client, temp_db_with_users):
    """
    GET /api/v1/users
    Should return a list of users and a 200 OK status.
    """
    # Given
    from datetime import datetime
    iso_datetime_str = datetime.now().isoformat()
    conn = sqlite3.connect(temp_db_with_users)
    cursor = conn.cursor()
    # Update the created_at to an ISO formatted string for test consistency
    cursor.execute("UPDATE users SET created_at = ? WHERE mastodon_id = ?", (iso_datetime_str, '12345'))
    cursor.execute("UPDATE users SET created_at = ? WHERE mastodon_id = ?", (iso_datetime_str, '67890'))
    conn.commit()
    conn.close()

    with client.session_transaction() as sess:
        sess['user_id'] = 'test_admin' # Simulate logged in admin

    # When
    response = client.get('/api/v1/users')

    # Then
    assert response.status_code == 200
    data = response.get_json()
    assert 'users' in data
    assert len(data['users']) >= 2 # At least the two users we inserted
    assert any(u['username'] == 'testuser1' for u in data['users'])
    assert any(u['username'] == 'testuser2' for u in data['users'])

def test_get_users_requires_auth(client):
    """
    GET /api/v1/users
    Should return 401 Unauthorized if not authenticated.
    """
    # When
    response = client.get('/api/v1/users')

    # Then
    assert response.status_code == 401
    assert 'Unauthorized' in response.get_json()['error']


def test_get_user_by_id_returns_200_and_user_detail(client, temp_db_with_users):
    """
    GET /api/v1/users/{id}
    Should return user detail and 200 OK status.
    """
    # Given
    from datetime import datetime
    iso_datetime_str = datetime.now().isoformat()
    conn = sqlite3.connect(temp_db_with_users)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET created_at = ? WHERE mastodon_id = ?", (iso_datetime_str, '12345'))
    conn.commit()
    conn.close()

    with client.session_transaction() as sess:
        sess['user_id'] = 'test_admin'

    # When
    response = client.get('/api/v1/users/12345')

    # Then
    assert response.status_code == 200
    data = response.get_json()
    assert 'user' in data
    assert data['user']['mastodon_id'] == '12345'
    assert data['user']['username'] == 'testuser1'


def test_get_user_by_id_returns_404_if_not_found(client, temp_db_with_users):
    """
    GET /api/v1/users/{id}
    Should return 404 Not Found if user does not exist.
    """
    # Given
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_admin'

    # When
    response = client.get('/api/v1/users/nonexistent')

    # Then
    assert response.status_code == 404
    assert 'User not found' in response.get_json()['error']


def test_patch_user_role_returns_200_and_updates_role(client, temp_db_with_users):
    """
    PATCH /api/v1/users/{id}/role
    Should update user role and return 200 OK status.
    """
    # Given
    from admin_web.services.user_service import UserService
    user_service = UserService(temp_db_with_users)
    original_user = user_service.get_user('12345')
    assert original_user.role == 'user'

    with client.session_transaction() as sess:
        sess['user_id'] = 'test_admin'

    update_data = {
        "role": "moderator"
    }

    # When
    response = client.patch('/api/v1/users/12345/role',
                            data=json.dumps(update_data),
                            content_type='application/json')

    # Then
    assert response.status_code == 200
    data = response.get_json()
    assert data['user']['mastodon_id'] == '12345'
    assert data['user']['role'] == 'moderator'

    # Verify in DB
    updated_user = user_service.get_user('12345')
    assert updated_user.role == 'moderator'


def test_patch_user_role_returns_400_on_invalid_role(client, temp_db_with_users):
    """
    PATCH /api/v1/users/{id}/role
    Should return 400 Bad Request on invalid role.
    """
    # Given
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_admin'

    update_data = {
        "role": "invalid_role"
    }

    # When
    response = client.patch('/api/v1/users/12345/role',
                            data=json.dumps(update_data),
                            content_type='application/json')

    # Then
    assert response.status_code == 400
    assert '유효하지 않은 역할입니다' in response.get_json()['error']


def test_patch_user_role_requires_auth(client):
    """
    PATCH /api/v1/users/{id}/role
    Should return 401 Unauthorized if not authenticated.
    """
    # When
    response = client.patch('/api/v1/users/12345/role',
                            data=json.dumps({"role": "moderator"}),
                            content_type='application/json')

    # Then
    assert response.status_code == 401
    assert 'Unauthorized' in response.get_json()['error']

