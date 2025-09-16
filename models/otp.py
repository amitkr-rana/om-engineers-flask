from database import db
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime
import random
import string

class OTP(db.Model):
    __tablename__ = 'otps'

    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), nullable=False, index=True)
    otp_code = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_verified = Column(db.Boolean, default=False)
    attempts = Column(Integer, default=0)

    def __init__(self, phone_number, otp_length=6, expiry_minutes=10):
        self.phone_number = phone_number
        self.otp_code = self.generate_otp(otp_length)
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(minutes=expiry_minutes)
        self.is_verified = False
        self.attempts = 0

    @staticmethod
    def generate_otp(length=6):
        """Generate a random numeric OTP"""
        return ''.join(random.choices(string.digits, k=length))

    @classmethod
    def create_new_otp(cls, phone_number, otp_length=6, expiry_minutes=10):
        """Create a new OTP for the given phone number"""
        # Delete any existing OTPs for this phone number
        cls.query.filter_by(phone_number=phone_number).delete()

        # Create new OTP
        otp = cls(phone_number, otp_length, expiry_minutes)
        db.session.add(otp)
        db.session.commit()
        return otp

    @classmethod
    def verify_otp(cls, phone_number, otp_code):
        """Verify OTP for a phone number"""
        otp_record = cls.query.filter_by(
            phone_number=phone_number,
            is_verified=False
        ).first()

        if not otp_record:
            return False, "OTP not found or already verified"

        # Check if OTP has expired
        if datetime.utcnow() > otp_record.expires_at:
            return False, "OTP has expired"

        # Increment attempts
        otp_record.attempts += 1

        # Check max attempts (limit to 5)
        if otp_record.attempts > 5:
            return False, "Too many invalid attempts"

        # Verify OTP code
        if otp_record.otp_code == otp_code:
            otp_record.is_verified = True
            db.session.commit()
            return True, "OTP verified successfully"
        else:
            db.session.commit()
            return False, "Invalid OTP code"

    @classmethod
    def cleanup_expired_otps(cls):
        """Clean up expired OTPs"""
        expired_otps = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for otp in expired_otps:
            db.session.delete(otp)
        db.session.commit()
        return len(expired_otps)

    def is_expired(self):
        """Check if OTP is expired"""
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_verified': self.is_verified,
            'attempts': self.attempts,
            'is_expired': self.is_expired()
        }