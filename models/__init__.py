# Import all models to ensure they are registered with SQLAlchemy
from .customer_db import Customer
from .customer_auth import CustomerAuth
from .service_db import Service
from .appointment_db import Appointment, AppointmentStatus, AppointmentType
from .otp import OTP

# Export for easier imports
__all__ = ['Customer', 'CustomerAuth', 'Service', 'Appointment', 'AppointmentStatus', 'AppointmentType', 'OTP']