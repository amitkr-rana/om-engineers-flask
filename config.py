import os
from pathlib import Path
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'om-engineers-secret-key-2024'

    # Authentication configuration
    AUTH_TOKEN_EXPIRY_HOURS = 24 * 30  # 30 days
    MAX_AUTH_ATTEMPTS = 5  # Max failed authentication attempts
    AUTH_RATE_LIMIT = 10  # Max auth requests per minute

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