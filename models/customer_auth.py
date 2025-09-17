from database import db
from datetime import datetime, timedelta
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import secrets
import string


class CustomerAuth(db.Model):
    """Authentication model for customers - separate from main Customer table"""
    __tablename__ = 'customer_auth'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), unique=True, nullable=False, index=True)

    # Authentication fields
    auth_key: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    auth_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Customer
    customer = relationship("Customer", backref="auth_record")

    @staticmethod
    def generate_auth_key() -> str:
        """Generate a unique 16-digit authentication key"""
        while True:
            # Generate 16-digit key using digits only
            auth_key = ''.join(secrets.choice(string.digits) for _ in range(16))
            # Ensure it doesn't already exist
            if not CustomerAuth.query.filter_by(auth_key=auth_key).first():
                return auth_key

    @staticmethod
    def generate_auth_token() -> str:
        """Generate a secure authentication token"""
        return secrets.token_urlsafe(48)  # 64 character token

    def create_auth_token(self, hours_valid: int = 24 * 30) -> str:
        """Create and store a new authentication token"""
        self.auth_token = self.generate_auth_token()
        self.token_expires_at = datetime.utcnow() + timedelta(hours=hours_valid)
        self.last_login = datetime.utcnow()
        return self.auth_token

    def is_token_valid(self) -> bool:
        """Check if the current token is valid and not expired"""
        if not self.auth_token or not self.token_expires_at:
            return False
        return datetime.utcnow() < self.token_expires_at and self.is_active

    def revoke_token(self):
        """Revoke the current authentication token"""
        self.auth_token = None
        self.token_expires_at = None

    @classmethod
    def get_or_create_for_customer(cls, customer_id: int):
        """Get or create authentication record for a customer"""
        auth_record = cls.query.filter_by(customer_id=customer_id).first()

        if not auth_record:
            auth_record = cls(
                customer_id=customer_id,
                auth_key=cls.generate_auth_key()
            )
            db.session.add(auth_record)
            db.session.commit()

        return auth_record

    @classmethod
    def get_by_auth_key(cls, auth_key: str):
        """Get authentication record by auth key"""
        return cls.query.filter_by(auth_key=auth_key, is_active=True).first()

    @classmethod
    def get_by_auth_token(cls, token: str):
        """Get authentication record by token if valid"""
        auth_record = cls.query.filter_by(auth_token=token, is_active=True).first()
        if auth_record and auth_record.is_token_valid():
            return auth_record
        return None

    @classmethod
    def get_customer_by_auth_key(cls, auth_key: str):
        """Get customer by authentication key"""
        auth_record = cls.get_by_auth_key(auth_key)
        return auth_record.customer if auth_record else None

    @classmethod
    def get_customer_by_auth_token(cls, token: str):
        """Get customer by authentication token if valid"""
        auth_record = cls.get_by_auth_token(token)
        return auth_record.customer if auth_record else None

    def to_dict(self) -> dict:
        """Convert auth record to dictionary"""
        return {
            'customer_id': self.customer_id,
            'auth_key': self.auth_key,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __str__(self) -> str:
        return f"CustomerAuth(customer_id={self.customer_id}, auth_key='{self.auth_key}')"

    def __repr__(self) -> str:
        return self.__str__()