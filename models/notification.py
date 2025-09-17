from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import db
from datetime import datetime
from enum import Enum

class NotificationType(Enum):
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    SERVICE_COMPLETED = "service_completed"
    PAYMENT_DUE = "payment_due"
    SPECIAL_OFFER = "special_offer"
    SYSTEM_UPDATE = "system_update"
    SERVICE_SCHEDULED = "service_scheduled"
    SERVICE_CANCELLED = "service_cancelled"

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=True)

    # Notification details
    notification_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    # Metadata
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Optional action
    action_text = Column(String(100), nullable=True)  # e.g., "View Appointment Details", "Book Now"
    action_url = Column(String(500), nullable=True)   # e.g., "/appointment/123", "/book"

    # Relationships
    customer = relationship("Customer", backref="notifications")
    appointment = relationship("Appointment", backref="notifications")

    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'appointment_id': self.appointment_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'action_text': self.action_text,
            'action_url': self.action_url,
            'time_ago': self.get_time_ago()
        }

    def get_time_ago(self):
        """Get human-readable time difference"""
        if not self.created_at:
            return "Unknown"

        now = datetime.utcnow()
        diff = now - self.created_at

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    def get_icon_class(self):
        """Get CSS icon class based on notification type"""
        icon_map = {
            NotificationType.APPOINTMENT_CONFIRMED.value: "calendar-check",
            NotificationType.SERVICE_COMPLETED.value: "check-circle",
            NotificationType.PAYMENT_DUE.value: "credit-card",
            NotificationType.SPECIAL_OFFER.value: "tag",
            NotificationType.SYSTEM_UPDATE.value: "bell",
            NotificationType.SERVICE_SCHEDULED.value: "calendar",
            NotificationType.SERVICE_CANCELLED.value: "x-circle"
        }
        return icon_map.get(self.notification_type, "bell")

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()

    @classmethod
    def create_notification(cls, customer_id, notification_type, title, message,
                          appointment_id=None, action_text=None, action_url=None):
        """Create a new notification"""
        notification = cls(
            customer_id=customer_id,
            appointment_id=appointment_id,
            notification_type=notification_type,
            title=title,
            message=message,
            action_text=action_text,
            action_url=action_url
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @classmethod
    def get_unread_count(cls, customer_id):
        """Get count of unread notifications for a customer"""
        return cls.query.filter_by(customer_id=customer_id, is_read=False).count()

    @classmethod
    def get_customer_notifications(cls, customer_id, limit=50):
        """Get notifications for a customer, ordered by newest first"""
        return cls.query.filter_by(customer_id=customer_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()

    @classmethod
    def mark_all_as_read(cls, customer_id):
        """Mark all notifications as read for a customer"""
        cls.query.filter_by(customer_id=customer_id, is_read=False)\
                 .update({'is_read': True, 'read_at': datetime.utcnow()})
        db.session.commit()