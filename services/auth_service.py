from typing import Optional, Tuple
from models.customer_db import Customer
from models.customer_auth import CustomerAuth
from database import db
from datetime import datetime


class AuthService:
    """Service class for handling authentication operations"""

    @staticmethod
    def authenticate_after_otp(phone_number: str) -> Tuple[Optional[Customer], str]:
        """
        Handle authentication after successful OTP verification.
        Returns (customer, auth_token) or (None, error_message)
        """
        try:
            # Look for existing customers with this phone number
            customers = Customer.get_all_by_phone(phone_number)

            if len(customers) == 0:
                # Create new customer for first-time user
                customer, created = Customer.get_or_create(
                    name=f"User {phone_number[-4:]}",  # Default name
                    email="",
                    phone=phone_number,
                    address=""
                )

                # Create or get auth record
                auth_record = CustomerAuth.get_or_create_for_customer(customer.id)
                token = auth_record.create_auth_token()
                db.session.commit()

                return customer, token

            elif len(customers) == 1:
                # Single customer - authenticate directly
                customer = customers[0]

                # Get or create auth record
                auth_record = CustomerAuth.get_or_create_for_customer(customer.id)
                token = auth_record.create_auth_token()
                db.session.commit()

                return customer, token

            else:
                # Multiple customers - return the first one for now
                # In a more complex system, this could show a selection screen
                customer = customers[0]

                auth_record = CustomerAuth.get_or_create_for_customer(customer.id)
                token = auth_record.create_auth_token()
                db.session.commit()

                return customer, token

        except Exception as e:
            db.session.rollback()
            return None, f"Authentication error: {str(e)}"

    @staticmethod
    def validate_token(token: str) -> Optional[Customer]:
        """
        Validate an authentication token and return the customer if valid.
        Returns None if token is invalid or expired.
        """
        if not token:
            print(f"  validate_token: No token provided")
            return None

        try:
            print(f"  validate_token: Checking token: {token[:20]}...")
            customer = CustomerAuth.get_customer_by_auth_token(token)
            print(f"  validate_token: Customer found: {customer}")
            return customer
        except Exception as e:
            print(f"  validate_token: Exception: {e}")
            return None

    @staticmethod
    def validate_auth_key(auth_key: str) -> Optional[Customer]:
        """
        Validate an authentication key and return the customer if valid.
        Returns None if key is invalid.
        """
        if not auth_key or len(auth_key) != 16:
            print(f"  validate_auth_key: Invalid key format: {auth_key}")
            return None

        try:
            print(f"  validate_auth_key: Checking key: {auth_key}")
            customer = CustomerAuth.get_customer_by_auth_key(auth_key)
            print(f"  validate_auth_key: Customer found: {customer}")
            return customer
        except Exception as e:
            print(f"  validate_auth_key: Exception: {e}")
            return None

    @staticmethod
    def refresh_token(customer: Customer) -> str:
        """
        Generate a new authentication token for an existing customer.
        """
        try:
            auth_record = CustomerAuth.get_or_create_for_customer(customer.id)
            token = auth_record.create_auth_token()
            db.session.commit()
            return token
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def revoke_token(customer: Customer):
        """
        Revoke the current authentication token for a customer.
        """
        try:
            auth_record = CustomerAuth.query.filter_by(customer_id=customer.id).first()
            if auth_record:
                auth_record.revoke_token()
                db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_customer_from_request_headers(request) -> Optional[Customer]:
        """
        Extract and validate customer from request headers.
        Looks for 'Authorization' header with 'Bearer <token>' format
        or 'X-Auth-Token' header with token directly.
        """
        # Try Authorization header first (Bearer token format)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            return AuthService.validate_token(token)

        # Try X-Auth-Token header
        token = request.headers.get('X-Auth-Token')
        if token:
            return AuthService.validate_token(token)

        # Try auth_key from headers
        auth_key = request.headers.get('X-Auth-Key')
        if auth_key:
            return AuthService.validate_auth_key(auth_key)

        return None

    @staticmethod
    def get_customer_from_request_params(request) -> Optional[Customer]:
        """
        Extract and validate customer from request parameters.
        Looks for 'token' or 'auth_key' parameters.
        """
        # Try token parameter
        token = request.args.get('token') or request.form.get('token')
        if token:
            return AuthService.validate_token(token)

        # Try auth_key parameter
        auth_key = request.args.get('auth_key') or request.form.get('auth_key')
        if auth_key:
            return AuthService.validate_auth_key(auth_key)

        return None

    @staticmethod
    def get_customer_from_request(request) -> Optional[Customer]:
        """
        Extract and validate customer from request (headers first, then params).
        """
        # Try headers first (more secure)
        customer = AuthService.get_customer_from_request_headers(request)
        if customer:
            return customer

        # Fallback to parameters (less secure but more convenient)
        return AuthService.get_customer_from_request_params(request)