from database import db
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from typing import List

class Service(db.Model):
    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    duration: Mapped[str] = mapped_column(String(50), nullable=False)
    price_range: Mapped[str] = mapped_column(String(50), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), default="🔧")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with appointments - using string reference
    appointments = db.relationship('Appointment', back_populates='service')

    def to_dict(self) -> dict:
        """Convert service to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'duration': self.duration,
            'price_range': self.price_range,
            'icon': self.icon,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def activate(self):
        """Activate the service"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def deactivate(self):
        """Deactivate the service"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        db.session.commit()

    @classmethod
    def get_all(cls, active_only: bool = True):
        """Get all services"""
        query = cls.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    @classmethod
    def get_by_category(cls, category: str, active_only: bool = True):
        """Get services by category"""
        query = cls.query.filter(cls.category.ilike(f'%{category}%'))
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    @classmethod
    def search(cls, query_text: str, active_only: bool = True):
        """Search services by name, description, or category"""
        query = cls.query.filter(
            db.or_(
                cls.name.ilike(f'%{query_text}%'),
                cls.description.ilike(f'%{query_text}%'),
                cls.category.ilike(f'%{query_text}%')
            )
        )
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    @classmethod
    def get_categories(cls, active_only: bool = True):
        """Get all unique service categories"""
        query = db.session.query(cls.category).distinct()
        if active_only:
            query = query.filter_by(is_active=True)
        return [category[0] for category in query.all()]

    def __str__(self) -> str:
        return f"Service(id={self.id}, name='{self.name}', category='{self.category}')"

    def __repr__(self) -> str:
        return self.__str__()