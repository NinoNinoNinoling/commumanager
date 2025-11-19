"""Database connection utilities"""
import sqlite3
import psycopg2
from contextlib import contextmanager
from flask import current_app


@contextmanager
def get_economy_db():
    """SQLite economy.db 연결"""
    conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_mastodon_db():
    """PostgreSQL 마스토돈 DB 연결 (읽기 전용)"""
    conn = psycopg2.connect(
        host=current_app.config.get('POSTGRES_HOST', 'localhost'),
        port=current_app.config.get('POSTGRES_PORT', 5432),
        database=current_app.config.get('POSTGRES_DB', 'mastodon'),
        user=current_app.config.get('POSTGRES_USER', 'mastodon'),
        password=current_app.config.get('POSTGRES_PASSWORD', ''),
    )
    conn.set_session(readonly=True, autocommit=True)
    try:
        yield conn
    finally:
        conn.close()
