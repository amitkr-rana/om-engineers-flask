from database import db
from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from typing import List

class Customer(db.Model):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with appointments - using string reference
    appointments = db.relationship('Appointment', back_populates='customer', cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        """Convert customer to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def get_by_email(cls, email: str):
        """Get customer by email"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_phone(cls, phone: str):
        """Get customer by phone number"""
        # Clean phone number for comparison
        clean_phone = ''.join(filter(str.isdigit, phone))
        customers = cls.query.all()
        for customer in customers:
            customer_clean_phone = ''.join(filter(str.isdigit, customer.phone))
            if customer_clean_phone == clean_phone:
                return customer
        return None

    @classmethod
    def search(cls, query: str):
        """Search customers by name, email, or phone"""
        return cls.query.filter(
            db.or_(
                cls.name.ilike(f'%{query}%'),
                cls.email.ilike(f'%{query}%'),
                cls.phone.ilike(f'%{query}%')
            )
        ).all()

    @classmethod
    def get_or_create(cls, name: str, email: str, phone: str, address: str = ""):
        """Get existing customer or create new one. Returns (customer, created)"""
        # Try to find existing customer by email or phone
        existing = None
        if email:
            existing = cls.get_by_email(email)
        if not existing:
            existing = cls.get_by_phone(phone)

        if existing:
            # Update existing customer info if provided
            if existing.name != name:
                existing.name = name
            if existing.address != address and address:
                existing.address = address
            if email and existing.email != email:
                existing.email = email
            if existing.phone != phone:
                existing.phone = phone
            existing.updated_at = datetime.utcnow()

            try:
                db.session.commit()
                return existing, False
            except Exception:
                db.session.rollback()
                return existing, False
        else:
            # Create new customer
            new_customer = cls(name=name, email=email, phone=phone, address=address)
            db.session.add(new_customer)
            try:
                db.session.commit()
                return new_customer, True
            except Exception:
                db.session.rollback()
                raise

    def __str__(self) -> str:
        return f"Customer(id={self.id}, name='{self.name}', email='{self.email}')"

    def __repr__(self) -> str:
        return self.__str__()