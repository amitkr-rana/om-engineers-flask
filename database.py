from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Initialize default data
        initialize_default_data()

def initialize_default_data():
    """Initialize default data - currently empty to allow fresh population"""
    # Import all models to ensure proper registration
    from models import Service, Customer, Appointment, OTP

    # No default services - admin will populate via web interface
    print("Database tables created successfully! Ready for admin population.")

def reset_database():
    """Reset the database - useful for development"""
    db.drop_all()
    db.create_all()
    initialize_default_data()
    print("Database reset successfully!")