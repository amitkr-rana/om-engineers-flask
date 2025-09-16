import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'om-engineers-secret-key-2024'

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