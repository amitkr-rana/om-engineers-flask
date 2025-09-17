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
    from models import Service, Customer, Appointment, OTP, CustomerAuth

    # Migrate existing customers to have auth records
    migrate_existing_customers()

    # No default services - admin will populate via web interface
    print("Database tables created successfully! Ready for admin population.")

def migrate_existing_customers():
    """Create auth records for existing customers that don't have them"""
    try:
        from models import Customer, CustomerAuth

        # Find customers without auth records
        customers_without_auth = db.session.query(Customer).outerjoin(CustomerAuth).filter(CustomerAuth.customer_id == None).all()

        if customers_without_auth:
            print(f"Creating auth records for {len(customers_without_auth)} customers...")

            for customer in customers_without_auth:
                CustomerAuth.get_or_create_for_customer(customer.id)

            print(f"Successfully created auth records for {len(customers_without_auth)} customers!")
        else:
            print("All customers already have auth records.")

    except Exception as e:
        print(f"Migration error (this is normal on first run): {e}")
        db.session.rollback()

def reset_database():
    """Reset the database - useful for development"""
    db.drop_all()
    db.create_all()
    initialize_default_data()
    print("Database reset successfully!")