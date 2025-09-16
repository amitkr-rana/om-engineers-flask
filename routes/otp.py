from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from services.otp_service import OTPService
from models.otp import OTP
from models.customer_db import Customer
from database import db
from datetime import datetime

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
            # Create or update customer record in database
            try:
                # Check if customer already exists by phone
                existing_customer = Customer.get_by_phone(phone_number)

                if existing_customer:
                    # Update existing customer
                    existing_customer.name = customer_name
                    existing_customer.updated_at = datetime.utcnow()
                    db.session.commit()
                    customer = existing_customer
                else:
                    # Create new customer
                    customer = Customer(
                        name=customer_name,
                        email=None,
                        phone=phone_number,
                        address=""
                    )
                    db.session.add(customer)
                    db.session.commit()

                # Store customer information in session
                session['customer_id'] = customer.id
                session['customer_phone'] = customer.phone

            except Exception as e:
                # Rollback any partial changes
                db.session.rollback()

                # Fallback - store in session only
                session['customer_name'] = customer_name
                session['customer_phone'] = phone_number

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