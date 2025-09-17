import os
from pathlib import Path
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'om-engineers-secret-key-2024'

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)  # Session lasts 30 days
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # True in production with HTTPS
    SESSION_COOKIE_SAMESITE = 'None' if os.environ.get('FLASK_ENV') == 'production' else 'Lax'  # Required for iframe embedding in prod
    SESSION_COOKIE_DOMAIN = None  # Allow cross-domain in iframe

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR / "om_engineers.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # App settings
    APP_NAME = 'Om Engineers'
    APP_TAGLINE = 'Your Equipment, Our Expertise'
    APP_DESCRIPTION = 'Schedule a repair service with ease. Our skilled professionals are ready to assist you.'

    # Contact information
    CONTACT_PHONE = '+917762924431'
    CONTACT_EMAIL = 'omengineers324@gmail.com'
    CONTACT_ADDRESS = 'Khatanga Ranchi, Jharkhand 834009'

    # Fast2SMS API Configuration
    FAST2SMS_API_KEY = '4arM7o4FY7pK5cyjUlrBcXa5UlcmYlJZGrbrlZsuQ0d8ZQ5Syvs3xe6JSZgU'

    # OTP Configuration
    OTP_EXPIRY_MINUTES = 10  # OTP valid for 10 minutes
    OTP_LENGTH = 6  # 6 digit OTP