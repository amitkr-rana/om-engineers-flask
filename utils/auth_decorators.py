from functools import wraps
from flask import request, jsonify, g
from typing import Optional
from services.auth_service import AuthService
from models.customer_db import Customer


def require_auth(f):
    """
    Decorator to require authentication for a route.
    Sets g.current_customer if authentication is successful.
    Returns 401 JSON response if authentication fails.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        customer = AuthService.get_customer_from_request(request)

        if not customer:
            return jsonify({
                'success': False,
                'message': 'Authentication required. Please provide a valid token or auth key.',
                'error_code': 'AUTH_REQUIRED'
            }), 401

        # Set current customer in Flask's g object for use in the route
        g.current_customer = customer

        return f(*args, **kwargs)

    return decorated_function


def require_auth_optional(f):
    """
    Decorator that optionally authenticates a user.
    Sets g.current_customer if authentication is successful, but doesn't fail if not.
    Useful for routes that can work with or without authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        customer = AuthService.get_customer_from_request(request)
        g.current_customer = customer  # Will be None if not authenticated
        return f(*args, **kwargs)

    return decorated_function


def require_customer_match(customer_id_param: str = 'customer_id'):
    """
    Decorator to ensure the authenticated customer matches a specific customer ID.

    Args:
        customer_id_param: The name of the parameter containing the customer ID to match
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            customer = AuthService.get_customer_from_request(request)

            if not customer:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required.',
                    'error_code': 'AUTH_REQUIRED'
                }), 401

            # Get customer ID from route parameters or form data
            target_customer_id = kwargs.get(customer_id_param) or request.form.get(customer_id_param) or request.args.get(customer_id_param)

            if not target_customer_id:
                return jsonify({
                    'success': False,
                    'message': f'Missing {customer_id_param} parameter.',
                    'error_code': 'MISSING_PARAMETER'
                }), 400

            # Convert to int for comparison
            try:
                target_customer_id = int(target_customer_id)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid {customer_id_param} format.',
                    'error_code': 'INVALID_PARAMETER'
                }), 400

            # Check if the authenticated customer matches the target customer
            if customer.id != target_customer_id:
                return jsonify({
                    'success': False,
                    'message': 'Access denied. You can only access your own data.',
                    'error_code': 'ACCESS_DENIED'
                }), 403

            g.current_customer = customer
            return f(*args, **kwargs)

        return decorated_function
    return decorator


def get_current_customer() -> Optional[Customer]:
    """
    Helper function to get the current authenticated customer from Flask's g object.
    Returns None if no customer is authenticated.
    """
    return getattr(g, 'current_customer', None)


def get_auth_response_data(customer: Customer, token: str) -> dict:
    """
    Helper function to create standardized authentication response data.

    Args:
        customer: The authenticated customer
        token: The authentication token

    Returns:
        dict: Standardized response data for authentication success
    """
    from models.customer_auth import CustomerAuth

    # Get auth record to include auth_key and expiration
    auth_record = CustomerAuth.query.filter_by(customer_id=customer.id).first()

    return {
        'success': True,
        'message': 'Authentication successful',
        'customer': {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'auth_key': auth_record.auth_key if auth_record else None,
            'last_login': auth_record.last_login.isoformat() if auth_record and auth_record.last_login else None
        },
        'auth': {
            'token': token,
            'expires_at': auth_record.token_expires_at.isoformat() if auth_record and auth_record.token_expires_at else None
        }
    }