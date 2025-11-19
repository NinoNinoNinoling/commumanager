"""
pytest 설정 및 fixture

테스트용 임시 DB를 생성하고 테스트 후 삭제합니다.
"""
import os
import pytest
import sqlite3
import tempfile
from flask import Flask


@pytest.fixture(scope='session')
def test_db_path():
    """테스트용 임시 DB 경로"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # DB 초기화
    from init_db import init_database
    init_database(path)

    yield path

    # 테스트 후 삭제
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture(scope='function')
def db_conn(test_db_path):
    """테스트용 DB 연결 (함수마다 트랜잭션 롤백)"""
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    yield conn

    # 트랜잭션 롤백
    conn.rollback()
    conn.close()


@pytest.fixture(scope='function')
def app(test_db_path):
    """Flask 앱 fixture"""
    from admin_web.app import create_app

    app = create_app('testing')

    # 테스트용 설정 오버라이드
    app.config.update({
        'TESTING': True,
        'DATABASE_PATH': test_db_path,
        'SECRET_KEY': 'test-secret-key',
        'MASTODON_INSTANCE_URL': 'https://test.social',
        'MASTODON_CLIENT_ID': 'test-client-id',
        'MASTODON_CLIENT_SECRET': 'test-client-secret',
    })

    yield app


@pytest.fixture(scope='function')
def client(app):
    """Flask 테스트 클라이언트"""
    return app.test_client()


@pytest.fixture(scope='function')
def auth_client(client, app):
    """인증된 Flask 테스트 클라이언트"""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_123'
        sess['username'] = 'testuser'
        sess['access_token'] = 'test_token'

    return client


@pytest.fixture(scope='function')
def sample_user_data():
    """샘플 유저 데이터"""
    return {
        'mastodon_id': 'test_user_123',
        'username': 'testuser',
        'display_name': 'Test User',
        'role': 'user',
        'balance': 1000,
        'total_earned': 2000,
        'total_spent': 1000
    }


@pytest.fixture(scope='function')
def sample_transaction_data():
    """샘플 거래 데이터"""
    return {
        'user_id': 'test_user_123',
        'transaction_type': 'reply',
        'amount': 100,
        'description': '10개 답글 정산'
    }


@pytest.fixture(scope='function')
def sample_item_data():
    """샘플 아이템 데이터"""
    return {
        'name': '테스트 아이템',
        'description': '테스트용 아이템입니다',
        'price': 500,
        'category': '기타',
        'is_active': True
    }
