import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'om-engineers-secret-key-2024'

    # App settings
    APP_NAME = 'Om Engineers'
    APP_TAGLINE = 'Your Equipment, Our Expertise'
    APP_DESCRIPTION = 'Schedule a repair service with ease. Our skilled professionals are ready to assist you.'

    # Contact information
    CONTACT_PHONE = '+91-XXXX-XXXX'
    CONTACT_EMAIL = 'info@omengineers.com'

    # Service settings
    SERVICES = [
        {
            'id': 1,
            'name': 'Electrical Repair',
            'description': 'Complete electrical solutions for your home',
            'icon': '⚡',
            'duration': '2-4 hours',
            'price_range': '₹500 - ₹2000'
        },
        {
            'id': 2,
            'name': 'Plumbing Services',
            'description': 'Professional plumbing repairs and installations',
            'icon': '🔧',
            'duration': '1-3 hours',
            'price_range': '₹300 - ₹1500'
        },
        {
            'id': 3,
            'name': 'AC Repair & Service',
            'description': 'Air conditioning repair and maintenance',
            'icon': '❄️',
            'duration': '1-2 hours',
            'price_range': '₹800 - ₹3000'
        },
        {
            'id': 4,
            'name': 'Home Appliance Repair',
            'description': 'Repair for washing machines, refrigerators, and more',
            'icon': '🏠',
            'duration': '2-3 hours',
            'price_range': '₹600 - ₹2500'
        }
    ]