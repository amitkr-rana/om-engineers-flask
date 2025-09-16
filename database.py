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
    """Initialize default services data"""
    # Import all models to ensure proper registration
    from models import Service, Customer, Appointment

    # Check if services already exist
    if Service.query.first() is None:
        default_services = [
            {
                'name': 'Electrical Repair',
                'description': 'Complete electrical solutions for your equipment including wiring, outlets, and fixtures',
                'category': 'Electrical',
                'duration': '2-4 hours',
                'price_range': '₹500 - ₹2000',
                'icon': '⚡'
            },
            {
                'name': 'Plumbing Services',
                'description': 'Professional plumbing repairs and installations for all your water-related needs',
                'category': 'Plumbing',
                'duration': '1-3 hours',
                'price_range': '₹300 - ₹1500',
                'icon': '🔧'
            },
            {
                'name': 'AC Repair & Service',
                'description': 'Air conditioning repair, maintenance, and installation services',
                'category': 'HVAC',
                'duration': '1-2 hours',
                'price_range': '₹800 - ₹3000',
                'icon': '❄️'
            },
            {
                'name': 'Equipment Appliance Repair',
                'description': 'Repair services for washing machines, refrigerators, microwaves, and more',
                'category': 'Appliances',
                'duration': '2-3 hours',
                'price_range': '₹600 - ₹2500',
                'icon': '🏠'
            },
            {
                'name': 'Carpentry Services',
                'description': 'Furniture repair, custom woodwork, and carpentry solutions',
                'category': 'Carpentry',
                'duration': '3-6 hours',
                'price_range': '₹1000 - ₹5000',
                'icon': '🔨'
            },
            {
                'name': 'Painting Services',
                'description': 'Interior and exterior painting services for homes and offices',
                'category': 'Painting',
                'duration': '4-8 hours',
                'price_range': '₹1500 - ₹8000',
                'icon': '🎨'
            },
            {
                'name': 'Cleaning Services',
                'description': 'Deep cleaning, regular maintenance, and specialized cleaning services',
                'category': 'Cleaning',
                'duration': '2-4 hours',
                'price_range': '₹800 - ₹3000',
                'icon': '🧹'
            },
            {
                'name': 'Equipment Maintenance',
                'description': 'Regular maintenance and troubleshooting for industrial equipment',
                'category': 'Maintenance',
                'duration': '1-3 hours',
                'price_range': '₹1000 - ₹4000',
                'icon': '⚙️'
            }
        ]

        for service_data in default_services:
            service = Service(**service_data)
            db.session.add(service)

        try:
            db.session.commit()
            print("Default services initialized successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing services: {e}")

def reset_database():
    """Reset the database - useful for development"""
    db.drop_all()
    db.create_all()
    initialize_default_data()
    print("Database reset successfully!")