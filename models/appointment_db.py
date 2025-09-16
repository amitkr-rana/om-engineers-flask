from database import db
from datetime import datetime, date, time
from sqlalchemy import String, Text, Date, Time, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum

class AppointmentStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class AppointmentType(PyEnum):
    SERVICE = "service"
    QUOTATION = "quotation"
    CONSULTATION = "consultation"

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'), nullable=False)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    appointment_time: Mapped[time] = mapped_column(Time, nullable=False)
    appointment_type: Mapped[AppointmentType] = mapped_column(Enum(AppointmentType), default=AppointmentType.SERVICE)
    status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING, index=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    estimated_duration: Mapped[str] = mapped_column(String(50), nullable=True)
    estimated_cost: Mapped[str] = mapped_column(String(50), nullable=True)
    actual_cost: Mapped[str] = mapped_column(String(50), nullable=True)
    technician_notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships - using string references
    customer = db.relationship('Customer', back_populates='appointments')
    service = db.relationship('Service', back_populates='appointments')

    @property
    def appointment_datetime(self) -> datetime:
        """Get appointment as datetime object"""
        return datetime.combine(self.appointment_date, self.appointment_time)

    def to_dict(self) -> dict:
        """Convert appointment to dictionary representation"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'service_id': self.service_id,
            'appointment_date': self.appointment_date.isoformat(),
            'appointment_time': self.appointment_time.isoformat(),
            'appointment_datetime': self.appointment_datetime.isoformat(),
            'appointment_type': self.appointment_type.value,
            'status': self.status.value,
            'notes': self.notes,
            'address': self.address,
            'estimated_duration': self.estimated_duration,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'technician_notes': self.technician_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None
        }

    def confirm(self):
        """Confirm the appointment"""
        self.status = AppointmentStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def start_service(self):
        """Mark appointment as in progress"""
        self.status = AppointmentStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def complete(self, actual_cost: str = "", technician_notes: str = ""):
        """Complete the appointment"""
        self.status = AppointmentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if actual_cost:
            self.actual_cost = actual_cost
        if technician_notes:
            self.technician_notes = technician_notes
        db.session.commit()

    def cancel(self, reason: str = ""):
        """Cancel the appointment"""
        self.status = AppointmentStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if reason:
            self.technician_notes = f"Cancelled: {reason}"
        db.session.commit()

    def reschedule(self, new_date: date, new_time: time, reason: str = ""):
        """Reschedule the appointment"""
        self.appointment_date = new_date
        self.appointment_time = new_time
        self.status = AppointmentStatus.RESCHEDULED
        self.updated_at = datetime.utcnow()
        if reason:
            self.technician_notes = f"Rescheduled: {reason}"
        db.session.commit()

    @classmethod
    def get_by_customer(cls, customer_id: int):
        """Get appointments by customer ID"""
        return cls.query.filter_by(customer_id=customer_id).all()

    @classmethod
    def get_by_service(cls, service_id: int):
        """Get appointments by service ID"""
        return cls.query.filter_by(service_id=service_id).all()

    @classmethod
    def get_by_status(cls, status: AppointmentStatus):
        """Get appointments by status"""
        return cls.query.filter_by(status=status).all()

    @classmethod
    def get_by_date(cls, target_date: date):
        """Get appointments by date"""
        return cls.query.filter_by(appointment_date=target_date).all()

    @classmethod
    def get_by_date_range(cls, start_date: date, end_date: date):
        """Get appointments within date range"""
        return cls.query.filter(
            cls.appointment_date >= start_date,
            cls.appointment_date <= end_date
        ).all()

    @classmethod
    def get_upcoming(cls, days: int = 7):
        """Get upcoming appointments within specified days"""
        from datetime import date, timedelta
        today = date.today()
        end_date = today + timedelta(days=days)
        return cls.query.filter(
            cls.appointment_date >= today,
            cls.appointment_date <= end_date,
            cls.status.notin_([AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED])
        ).all()

    @classmethod
    def get_today(cls):
        """Get today's appointments"""
        return cls.get_by_date(date.today())

    @classmethod
    def search(cls, query: str):
        """Search appointments by notes, address, or technician notes"""
        return cls.query.filter(
            db.or_(
                cls.notes.ilike(f'%{query}%'),
                cls.address.ilike(f'%{query}%'),
                cls.technician_notes.ilike(f'%{query}%')
            )
        ).all()

    @classmethod
    def get_available_time_slots(cls, target_date: date, duration_hours: int = 2):
        """Get available time slots for a given date"""
        from datetime import time as dt_time

        # Working hours: 9 AM to 6 PM
        work_start = dt_time(9, 0)
        work_end = dt_time(18, 0)

        # Get all appointments for the date
        existing_appointments = cls.get_by_date(target_date)

        # Generate all possible time slots (every hour)
        available_slots = []
        current_hour = 9

        while current_hour <= (18 - duration_hours):
            slot_time = dt_time(current_hour, 0)
            slot_end_hour = current_hour + duration_hours

            # Check if this slot conflicts with existing appointments
            is_available = True
            for apt in existing_appointments:
                if apt.status in [AppointmentStatus.CANCELLED]:
                    continue

                apt_start_hour = apt.appointment_time.hour
                apt_end_hour = apt_start_hour + duration_hours

                # Check for overlap
                if not (slot_end_hour <= apt_start_hour or current_hour >= apt_end_hour):
                    is_available = False
                    break

            if is_available:
                available_slots.append(slot_time)

            current_hour += 1

        return available_slots

    @classmethod
    def get_statistics(cls):
        """Get appointment statistics"""
        total = cls.query.count()
        if total == 0:
            return {
                'total': 0,
                'pending': 0,
                'confirmed': 0,
                'completed': 0,
                'cancelled': 0,
                'completion_rate': 0.0
            }

        status_counts = {}
        for status in AppointmentStatus:
            status_counts[status.value] = cls.query.filter_by(status=status).count()

        completed = status_counts.get('completed', 0)
        completion_rate = (completed / total) * 100 if total > 0 else 0

        return {
            'total': total,
            'pending': status_counts.get('pending', 0),
            'confirmed': status_counts.get('confirmed', 0),
            'completed': completed,
            'cancelled': status_counts.get('cancelled', 0),
            'completion_rate': round(completion_rate, 2)
        }

    def __str__(self) -> str:
        return f"Appointment(id={self.id}, customer_id={self.customer_id}, date={self.appointment_date}, status={self.status.value})"

    def __repr__(self) -> str:
        return self.__str__()