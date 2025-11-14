import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""

    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///voting_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security Settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600)))

    # WTF Forms CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day;50 per hour')

    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@votingsystem.com')

    # SMS Configuration (Twilio)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  os.environ.get('UPLOAD_FOLDER', 'uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB default
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,pdf').split(','))

    # Password Policy
    MIN_PASSWORD_LENGTH = int(os.environ.get('MIN_PASSWORD_LENGTH', 8))
    REQUIRE_UPPERCASE = os.environ.get('REQUIRE_UPPERCASE', 'True').lower() == 'true'
    REQUIRE_LOWERCASE = os.environ.get('REQUIRE_LOWERCASE', 'True').lower() == 'true'
    REQUIRE_DIGITS = os.environ.get('REQUIRE_DIGITS', 'True').lower() == 'true'
    REQUIRE_SPECIAL_CHARS = os.environ.get('REQUIRE_SPECIAL_CHARS', 'True').lower() == 'true'

    # Election Settings
    ELECTION_START_DATE = os.environ.get('ELECTION_START_DATE')
    ELECTION_END_DATE = os.environ.get('ELECTION_END_DATE')
    ENABLE_LIVE_RESULTS = os.environ.get('ENABLE_LIVE_RESULTS', 'False').lower() == 'true'

    # Admin Configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@votingsystem.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Change this!

    # Blockchain Configuration (Phase 1)
    BLOCKCHAIN_ENABLED = os.environ.get('BLOCKCHAIN_ENABLED', 'False').lower() == 'true'
    BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK', 'mumbai')  # mumbai or polygon
    MUMBAI_RPC_URL = os.environ.get('MUMBAI_RPC_URL', '')
    POLYGON_RPC_URL = os.environ.get('POLYGON_RPC_URL', '')
    BLOCKCHAIN_PRIVATE_KEY = os.environ.get('BLOCKCHAIN_PRIVATE_KEY', '')

    # Contract addresses (set after deployment)
    VOTE_REGISTRY_ADDRESS = os.environ.get('VOTE_REGISTRY_ADDRESS', '')
    ELECTION_MANAGER_ADDRESS = os.environ.get('ELECTION_MANAGER_ADDRESS', '')
    VOTER_REGISTRY_ADDRESS = os.environ.get('VOTER_REGISTRY_ADDRESS', '')

    # Blockchain behavior
    BLOCKCHAIN_ASYNC = os.environ.get('BLOCKCHAIN_ASYNC', 'False').lower() == 'true'
    BLOCKCHAIN_FAIL_GRACEFULLY = os.environ.get('BLOCKCHAIN_FAIL_GRACEFULLY', 'True').lower() == 'true'
    BLOCKCHAIN_BATCH_SIZE = int(os.environ.get('BLOCKCHAIN_BATCH_SIZE', 50))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
