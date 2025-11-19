"""
Flask application configuration
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MASTODON_INSTANCE_URL = os.environ.get('MASTODON_INSTANCE_URL')
    MASTODON_CLIENT_ID = os.environ.get('MASTODON_CLIENT_ID')
    MASTODON_CLIENT_SECRET = os.environ.get('MASTODON_CLIENT_SECRET')
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'economy.db'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
