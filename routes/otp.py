from flask import Blueprint, request, jsonify, render_template
from services.otp_service import OTPService
from services.auth_service import AuthService
from models.otp import OTP
from models.customer_db import Customer
from utils.auth_decorators import get_auth_response_data
from database import db
from datetime import datetime

otp_bp = Blueprint('otp', __name__)

@otp_bp.route('/send', methods=['POST'])
def send_otp():
    """Send OTP to phone number"""
    try:
        data = request.get_json() if request.is_json else request.form
        phone_number = data.get('phone_number', '').strip()

        if not phone_number:
            return jsonify({
                'success': False,
                'message': 'Phone number is required'
            }), 400

        # Send OTP
        success, message = OTPService.send_otp(phone_number)

        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@otp_bp.route('/verify', methods=['POST'])
def verify_otp():
    """Verify OTP code and return authentication token"""
    try:
        data = request.get_json() if request.is_json else request.form
        phone_number = data.get('phone_number', '').strip()
        otp_code = data.get('otp_code', '').strip()

        if not phone_number or not otp_code:
            return jsonify({
                'success': False,
                'message': 'Phone number and OTP code are required',
                'error_code': 'MISSING_PARAMETERS'
            }), 400

        # Verify OTP
        success, message = OTPService.verify_otp(phone_number, otp_code)

        if success:
            # Authenticate user after successful OTP verification
            customer, token = AuthService.authenticate_after_otp(phone_number)

            if customer and token:
                # Return authentication data with dashboard URL
                auth_data = get_auth_response_data(customer, token)
                auth_data['dashboard_url'] = f"/dashboard?token={token}"
                auth_data['dashboard_url_with_key'] = f"/dashboard?auth_key={auth_data['customer']['auth_key']}"

                return jsonify(auth_data), 200
            else:
                return jsonify({
                    'success': False,
                    'message': token or 'Authentication failed',
                    'error_code': 'AUTH_FAILED'
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': message,
                'error_code': 'OTP_INVALID'
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'error_code': 'SERVER_ERROR'
        }), 500

@otp_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    """Refresh authentication token for a logged-in user"""
    try:
        # Get current customer from token
        customer = AuthService.get_customer_from_request(request)

        if not customer:
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'error_code': 'AUTH_REQUIRED'
            }), 401

        # Generate new token
        new_token = AuthService.refresh_token(customer)

        return jsonify(get_auth_response_data(customer, new_token)), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'error_code': 'SERVER_ERROR'
        }), 500

@otp_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user by revoking their authentication token"""
    try:
        # Get current customer from token
        customer = AuthService.get_customer_from_request(request)

        if customer:
            # Revoke the token
            AuthService.revoke_token(customer)

        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'error_code': 'SERVER_ERROR'
        }), 500

@otp_bp.route('/resend', methods=['POST'])
def resend_otp():
    """Resend OTP to phone number"""
    try:
        data = request.get_json() if request.is_json else request.form
        phone_number = data.get('phone_number', '').strip()

        if not phone_number:
            return jsonify({
                'success': False,
                'message': 'Phone number is required'
            }), 400

        # Resend OTP
        success, message = OTPService.resend_otp(phone_number)

        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@otp_bp.route('/status/<phone_number>')
def get_otp_status(phone_number):
    """Get OTP status for debugging (admin only)"""
    try:
        success, data = OTPService.get_otp_status(phone_number)

        return jsonify({
            'success': success,
            'data': data if success else None,
            'message': data if not success else 'OTP status retrieved'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@otp_bp.route('/test-auth')
def test_auth():
    """Test authentication - shows current customer if authenticated"""
    try:
        print(f"Test auth request:")
        print(f"  URL params: {request.args}")
        print(f"  Headers: {dict(request.headers)}")

        customer = AuthService.get_customer_from_request(request)
        print(f"  Customer result: {customer}")

        if customer:
            from models.customer_auth import CustomerAuth
            auth_record = CustomerAuth.query.filter_by(customer_id=customer.id).first()
            print(f"  Auth record: {auth_record}")

            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'customer': customer.to_dict(),
                'auth_info': auth_record.to_dict() if auth_record else None
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Not authenticated',
                'error_code': 'AUTH_REQUIRED'
            }), 401

    except Exception as e:
        print(f"  Test auth exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'error_code': 'SERVER_ERROR'
        }), 500

@otp_bp.route('/debug-db')
def debug_db():
    """Debug database state"""
    try:
        from models.customer_auth import CustomerAuth
        from models.customer_db import Customer

        # Get all customers and their auth records
        customers = Customer.query.all()
        auth_records = CustomerAuth.query.all()

        debug_info = {
            'customers_count': len(customers),
            'auth_records_count': len(auth_records),
            'customers': [{'id': c.id, 'name': c.name, 'phone': c.phone} for c in customers],
            'auth_records': [{'customer_id': a.customer_id, 'auth_key': a.auth_key, 'has_token': bool(a.auth_token)} for a in auth_records]
        }

        return jsonify({
            'success': True,
            'debug_info': debug_info
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@otp_bp.route('/test')
def test_page():
    """Test page for OTP functionality"""
    return render_template('otp/test.html')

@otp_bp.route('/cleanup', methods=['POST'])
def cleanup_expired():
    """Clean up expired OTPs (admin only)"""
    try:
        success, message = OTPService.cleanup_expired_otps()

        return jsonify({
            'success': success,
            'message': message
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500