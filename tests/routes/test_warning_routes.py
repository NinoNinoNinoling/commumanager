"""
WarningController tests
"""
import json
import pytest

@pytest.fixture
def temp_db_with_user(temp_db):
    """Fixture to create a temporary database with a user."""
    from init_db import initialize_database
    import sqlite3
    initialize_database(temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (mastodon_id, username, role) VALUES (?, ?, ?)", 
                   ('12345', 'testuser', 'user'))
    conn.commit()
    conn.close()
    return temp_db

def test_should_create_warning_manually(client, temp_db_with_user):
    """
    POST /api/v1/warnings
    Should create a warning manually and return 201 Created.
    """
    # Given
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_admin'

    warning_data = {
        "user_id": "12345",
        "warning_type": "activity",
        "message": "Manual warning for testing",
        "admin_name": "test_admin"
    }

    # When
    response = client.post('/api/v1/warnings',
                           data=json.dumps(warning_data),
                           content_type='application/json')

    # Then
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['warning']['user_id'] == '12345'
    assert data['warning']['warning_type'] == 'activity'
    assert data['warning']['message'] == "Manual warning for testing"
    assert data['user']['warning_count'] == 1

    # Verify in DB
    import sqlite3
    conn = sqlite3.connect(temp_db_with_user)
    cursor = conn.cursor()
    cursor.execute("SELECT warning_count FROM users WHERE mastodon_id = '12345'")
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM warnings WHERE user_id = '12345'")
    assert cursor.fetchone()[0] == 1
    conn.close()


def test_get_all_warnings_returns_200_and_list(client, temp_db_with_user):
    """
    GET /api/v1/warnings
    Should return a list of all warnings and a 200 OK status.
    """
    # Given: Create a warning first
    from admin_web.services.warning_service import WarningService
    service = WarningService(temp_db_with_user)
    service.issue_warning(
        user_id='12345',
        warning_type='activity',
        message='Test warning for list',
        admin_name='test_admin'
    )

    with client.session_transaction() as sess:
        sess['user_id'] = 'test_admin'

    # When
    response = client.get('/api/v1/warnings')

    # Then
    assert response.status_code == 200
    data = response.get_json()
    assert 'warnings' in data
    assert len(data['warnings']) >= 1
    assert any(w['user_id'] == '12345' for w in data['warnings'])


def test_get_user_warnings_returns_200_and_list(client, temp_db_with_user):
    """
    GET /api/v1/users/{id}/warnings
    Should return a list of warnings for a specific user and a 200 OK status.
    """
    # Given: Create a warning for '12345'
    from admin_web.services.warning_service import WarningService
    service = WarningService(temp_db_with_user)
    service.issue_warning(
        user_id='12345',
        warning_type='isolation',
        message='User specific warning',
        admin_name='test_admin'
    )

    with client.session_transaction() as sess:
        sess['user_id'] = 'test_admin'

    # When
    response = client.get('/api/v1/users/12345/warnings')

    # Then
    assert response.status_code == 200
    data = response.get_json()
    assert 'warnings' in data
    assert len(data['warnings']) >= 1
    assert all(w['user_id'] == '12345' for w in data['warnings'])
    assert any(w['warning_type'] == 'isolation' for w in data['warnings'])