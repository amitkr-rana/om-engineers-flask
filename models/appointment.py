from datetime import datetime, date, time
from typing import Dict, List, Optional, Tuple
from enum import Enum

class AppointmentStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class AppointmentType(Enum):
    SERVICE = "service"
    QUOTATION = "quotation"
    CONSULTATION = "consultation"

class Appointment:
    _appointments: Dict[int, 'Appointment'] = {}
    _next_id = 1

    def __init__(self, customer_id: int, service_id: int, appointment_date: date,
                 appointment_time: time, appointment_type: AppointmentType = AppointmentType.SERVICE,
                 notes: str = "", address: str = "", appointment_id: Optional[int] = None):
        self.id = appointment_id if appointment_id is not None else Appointment._next_id
        Appointment._next_id = max(Appointment._next_id, self.id) + 1

        self.customer_id = customer_id
        self.service_id = service_id
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.appointment_type = appointment_type
        self.status = AppointmentStatus.PENDING
        self.notes = notes
        self.address = address
        self.estimated_duration = ""
        self.estimated_cost = ""
        self.actual_cost = ""
        self.technician_notes = ""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at = None
        self.cancelled_at = None

        # Store in memory
        Appointment._appointments[self.id] = self

    @property
    def appointment_datetime(self) -> datetime:
        """Get appointment as datetime object"""
        return datetime.combine(self.appointment_date, self.appointment_time)

    def to_dict(self) -> Dict:
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

    def update(self, **kwargs) -> None:
        """Update appointment attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                if key == 'status' and isinstance(value, str):
                    setattr(self, key, AppointmentStatus(value))
                elif key == 'appointment_type' and isinstance(value, str):
                    setattr(self, key, AppointmentType(value))
                else:
                    setattr(self, key, value)
        self.updated_at = datetime.now()

    def confirm(self) -> None:
        """Confirm the appointment"""
        self.status = AppointmentStatus.CONFIRMED
        self.updated_at = datetime.now()

    def start_service(self) -> None:
        """Mark appointment as in progress"""
        self.status = AppointmentStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def complete(self, actual_cost: str = "", technician_notes: str = "") -> None:
        """Complete the appointment"""
        self.status = AppointmentStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        if actual_cost:
            self.actual_cost = actual_cost
        if technician_notes:
            self.technician_notes = technician_notes

    def cancel(self, reason: str = "") -> None:
        """Cancel the appointment"""
        self.status = AppointmentStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.updated_at = datetime.now()
        if reason:
            self.technician_notes = f"Cancelled: {reason}"

    def reschedule(self, new_date: date, new_time: time, reason: str = "") -> None:
        """Reschedule the appointment"""
        self.appointment_date = new_date
        self.appointment_time = new_time
        self.status = AppointmentStatus.RESCHEDULED
        self.updated_at = datetime.now()
        if reason:
            self.technician_notes = f"Rescheduled: {reason}"

    @classmethod
    def create(cls, customer_id: int, service_id: int, appointment_date: date,
               appointment_time: time, appointment_type: AppointmentType = AppointmentType.SERVICE,
               notes: str = "", address: str = "") -> 'Appointment':
        """Create a new appointment"""
        return cls(customer_id=customer_id, service_id=service_id,
                   appointment_date=appointment_date, appointment_time=appointment_time,
                   appointment_type=appointment_type, notes=notes, address=address)

    @classmethod
    def get_by_id(cls, appointment_id: int) -> Optional['Appointment']:
        """Get appointment by ID"""
        return cls._appointments.get(appointment_id)

    @classmethod
    def get_all(cls) -> List['Appointment']:
        """Get all appointments"""
        return list(cls._appointments.values())

    @classmethod
    def get_by_customer(cls, customer_id: int) -> List['Appointment']:
        """Get appointments by customer ID"""
        return [apt for apt in cls._appointments.values() if apt.customer_id == customer_id]

    @classmethod
    def get_by_service(cls, service_id: int) -> List['Appointment']:
        """Get appointments by service ID"""
        return [apt for apt in cls._appointments.values() if apt.service_id == service_id]

    @classmethod
    def get_by_status(cls, status: AppointmentStatus) -> List['Appointment']:
        """Get appointments by status"""
        return [apt for apt in cls._appointments.values() if apt.status == status]

    @classmethod
    def get_by_date(cls, target_date: date) -> List['Appointment']:
        """Get appointments by date"""
        return [apt for apt in cls._appointments.values() if apt.appointment_date == target_date]

    @classmethod
    def get_by_date_range(cls, start_date: date, end_date: date) -> List['Appointment']:
        """Get appointments within date range"""
        return [apt for apt in cls._appointments.values()
                if start_date <= apt.appointment_date <= end_date]

    @classmethod
    def get_upcoming(cls, days: int = 7) -> List['Appointment']:
        """Get upcoming appointments within specified days"""
        today = date.today()
        end_date = date.fromordinal(today.toordinal() + days)
        upcoming = cls.get_by_date_range(today, end_date)
        return [apt for apt in upcoming if apt.status not in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]]

    @classmethod
    def get_today(cls) -> List['Appointment']:
        """Get today's appointments"""
        return cls.get_by_date(date.today())

    @classmethod
    def search(cls, query: str) -> List['Appointment']:
        """Search appointments by notes, address, or technician notes"""
        query = query.lower().strip()
        results = []

        for appointment in cls._appointments.values():
            if (query in appointment.notes.lower() or
                query in appointment.address.lower() or
                query in appointment.technician_notes.lower()):
                results.append(appointment)

        return results

    @classmethod
    def get_available_time_slots(cls, target_date: date, duration_hours: int = 2) -> List[time]:
        """Get available time slots for a given date"""
        # Working hours: 9 AM to 6 PM
        work_start = time(9, 0)
        work_end = time(18, 0)

        # Get all appointments for the date
        existing_appointments = cls.get_by_date(target_date)

        # Generate all possible time slots (every hour)
        available_slots = []
        current_time = work_start

        while current_time <= time(work_end.hour - duration_hours, 0):
            slot_end = time(current_time.hour + duration_hours, current_time.minute)

            # Check if this slot conflicts with existing appointments
            is_available = True
            for apt in existing_appointments:
                if apt.status in [AppointmentStatus.CANCELLED]:
                    continue

                apt_start = apt.appointment_time
                apt_end = time(apt_start.hour + duration_hours, apt_start.minute)

                # Check for overlap
                if not (slot_end <= apt_start or current_time >= apt_end):
                    is_available = False
                    break

            if is_available:
                available_slots.append(current_time)

            # Move to next hour
            current_time = time(current_time.hour + 1, current_time.minute)

        return available_slots

    @classmethod
    def delete(cls, appointment_id: int) -> bool:
        """Delete appointment by ID"""
        if appointment_id in cls._appointments:
            del cls._appointments[appointment_id]
            return True
        return False

    @classmethod
    def get_statistics(cls) -> Dict:
        """Get appointment statistics"""
        total = len(cls._appointments)
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
            status_counts[status.value] = len(cls.get_by_status(status))

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