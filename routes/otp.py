from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from services.otp_service import OTPService
from models.otp import OTP
from models.customer_db import Customer
from database import db

otp_bp = Blueprint('otp', __name__)

@otp_bp.route('/send', methods=['POST'])
def send_otp():
    """Send OTP to phone number"""
    try:
        data = request.get_json() if request.is_json else request.form
        phone_number = data.get('phone_number', '').strip()
        customer_name = data.get('customer_name', '').strip()

        if not phone_number:
            return jsonify({
                'success': False,
                'message': 'Phone number is required'
            }), 400

        if not customer_name:
            return jsonify({
                'success': False,
                'message': 'Customer name is required'
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
    """Verify OTP code"""
    try:
        data = request.get_json() if request.is_json else request.form
        phone_number = data.get('phone_number', '').strip()
        otp_code = data.get('otp_code', '').strip()
        customer_name = data.get('customer_name', '').strip()

        if not phone_number or not otp_code:
            return jsonify({
                'success': False,
                'message': 'Phone number and OTP code are required'
            }), 400

        if not customer_name:
            return jsonify({
                'success': False,
                'message': 'Customer name is required'
            }), 400

        # Verify OTP
        success, message = OTPService.verify_otp(phone_number, otp_code)

        if success:
            # Create or update customer record
            try:
                customer, created = Customer.get_or_create(
                    name=customer_name,
                    email="",  # Will be updated later if needed
                    phone=phone_number,
                    address=""  # Will be updated later if needed
                )

                # Store customer ID in session
                session['customer_id'] = customer.id
                session['customer_name'] = customer.name
                session['customer_phone'] = customer.phone

            except Exception as e:
                # If customer creation fails, still allow login but log the error
                print(f"Error creating/updating customer: {str(e)}")

        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
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