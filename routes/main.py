from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, time
from models import Customer, Service, Appointment, AppointmentType
from services.auth_service import AuthService
from utils.auth_decorators import require_auth, get_current_customer, get_auth_response_data
from database import db
import requests
import re

main_bp = Blueprint('main', __name__)

def sanitize_text(text):
    """Sanitize and format text fields"""
    if not text:
        return ""

    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())

    # Remove special characters but keep common punctuation
    text = re.sub(r'[^\w\s\-\.\,\(\)\/]', '', text)

    # Title case for proper names
    text = text.title()

    return text

def sanitize_address_component(component):
    """Sanitize individual address components"""
    if not component:
        return ""

    # Basic sanitization
    component = re.sub(r'\s+', ' ', component.strip())

    # Remove unwanted characters but keep common punctuation
    component = re.sub(r'[^\w\s\-\.\,\(\)\/\#]', '', component)

    # Title case
    component = component.title()

    return component

@main_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@main_bp.route('/get-started')
def get_started():
    """OTP login page for accessing services"""
    return render_template('otp_login.html')

@main_bp.route('/get-started', methods=['POST'])
def get_started_post():
    """Handle get started form submission"""
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        service_id = request.form.get('service_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        notes = request.form.get('notes', '').strip()

        # Validate required fields
        if not all([name, email, phone, service_id, appointment_date, appointment_time]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('main.get_started'))

        # Validate service exists
        service = Service.query.get(int(service_id))
        if not service:
            flash('Invalid service selected', 'error')
            return redirect(url_for('main.get_started'))

        # Parse date and time
        try:
            parsed_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            parsed_time = datetime.strptime(appointment_time, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format', 'error')
            return redirect(url_for('main.get_started'))

        # Check if date is in the future
        if parsed_date < date.today():
            flash('Appointment date must be in the future', 'error')
            return redirect(url_for('main.get_started'))

        # Check if date is not too far in future (90 days)
        max_date = date.fromordinal(date.today().toordinal() + 90)
        if parsed_date > max_date:
            flash('Appointment date cannot be more than 90 days in the future', 'error')
            return redirect(url_for('main.get_started'))

        # Create or get customer
        customer, created = Customer.get_or_create(
            name=name,
            email=email,
            phone=phone,
            address=address
        )

        # Create appointment
        appointment = Appointment(
            customer_id=customer.id,
            service_id=service.id,
            appointment_date=parsed_date,
            appointment_time=parsed_time,
            appointment_type=AppointmentType.SERVICE,
            notes=notes,
            address=address
        )
        db.session.add(appointment)
        db.session.commit()

        # Success message
        flash(f'Service appointment scheduled successfully! Your appointment ID is #{appointment.id}', 'success')
        return redirect(url_for('main.appointment_confirmation', appointment_id=appointment.id))

    except Exception as e:
        flash('An error occurred while scheduling your appointment. Please try again.', 'error')
        return redirect(url_for('main.get_started'))

@main_bp.route('/request-quotation')
def request_quotation():
    """Request quotation form"""
    services = Service.get_all()
    return render_template('request_quotation.html', services=services)

@main_bp.route('/request-quotation', methods=['POST'])
def request_quotation_post():
    """Handle quotation request form submission"""
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        service_id = request.form.get('service_id')
        preferred_date = request.form.get('preferred_date')
        preferred_time = request.form.get('preferred_time')
        description = request.form.get('description', '').strip()

        # Validate required fields
        if not all([name, email, phone, address, service_id, description]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('main.request_quotation'))

        # Validate service exists
        service = Service.query.get(int(service_id))
        if not service:
            flash('Invalid service selected', 'error')
            return redirect(url_for('main.request_quotation'))

        # Parse date and time (optional for quotation)
        parsed_date = date.today()
        parsed_time = time(10, 0)  # Default to 10:00 AM

        if preferred_date:
            try:
                parsed_date = datetime.strptime(preferred_date, '%Y-%m-%d').date()
                if parsed_date < date.today():
                    parsed_date = date.today()
            except ValueError:
                parsed_date = date.today()

        if preferred_time:
            try:
                parsed_time = datetime.strptime(preferred_time, '%H:%M').time()
            except ValueError:
                parsed_time = time(10, 0)

        # Create or get customer
        customer, created = Customer.get_or_create(
            name=name,
            email=email,
            phone=phone,
            address=address
        )

        # Create quotation appointment
        appointment = Appointment(
            customer_id=customer.id,
            service_id=service.id,
            appointment_date=parsed_date,
            appointment_time=parsed_time,
            appointment_type=AppointmentType.QUOTATION,
            notes=f"Quotation request: {description}",
            address=address
        )
        db.session.add(appointment)
        db.session.commit()

        # Success message
        flash(f'Quotation request submitted successfully! Your request ID is #{appointment.id}', 'success')
        return redirect(url_for('main.appointment_confirmation', appointment_id=appointment.id))

    except Exception as e:
        flash('An error occurred while submitting your quotation request. Please try again.', 'error')
        return redirect(url_for('main.request_quotation'))

@main_bp.route('/appointment/<int:appointment_id>/confirmation')
def appointment_confirmation(appointment_id):
    """Appointment confirmation page"""
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        flash('Appointment not found', 'error')
        return redirect(url_for('main.index'))

    customer = Customer.query.get(appointment.customer_id)
    service = Service.query.get(appointment.service_id)

    return render_template('appointment_confirmation.html',
                         appointment=appointment,
                         customer=customer,
                         service=service)

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')


# Logout is now handled in OTP routes at /api/otp/logout

@main_bp.route('/dashboard')
def dashboard():
    """User dashboard - supports authentication via token/auth_key in headers or URL parameters"""
    # Debug: Print request parameters
    print(f"Dashboard access attempt:")
    print(f"  URL params: {request.args}")
    print(f"  Headers: {dict(request.headers)}")

    # Try to get authenticated customer
    customer = AuthService.get_customer_from_request(request)
    print(f"  Customer found: {customer}")

    if not customer:
        # If no authentication found, return JSON error for API calls or redirect for browser
        if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({
                'success': False,
                'message': 'Authentication required. Please provide a valid token or auth key.',
                'error_code': 'AUTH_REQUIRED'
            }), 401
        else:
            # For browser requests, redirect to login
            flash('Please log in to access your dashboard.', 'info')
            return redirect(url_for('main.get_started'))

    # Fetch upcoming appointments for the customer
    upcoming_appointments = []
    try:
        # Get appointments that are in the future and not cancelled
        all_appointments = Appointment.query.filter_by(customer_id=customer.id).all()
        now = datetime.now()
        upcoming_appointments = [
            apt for apt in all_appointments
            if apt.appointment_date >= now.date() and
            apt.status.value in ['pending', 'confirmed']
        ]
        # Sort by date and time
        upcoming_appointments.sort(key=lambda x: (x.appointment_date, x.appointment_time))
    except Exception as e:
        upcoming_appointments = []

    return render_template('user_dashboard.html',
                         customer_name=customer.name,
                         customer_phone=customer.phone,
                         customer=customer,
                         upcoming_appointments=upcoming_appointments)

@main_bp.route('/auth-test')
def auth_test():
    """Authentication test page - demonstrates complete OTP to dashboard flow"""
    return render_template('auth_test.html')

@main_bp.route('/profile/<auth_key>/update', methods=['POST'])
@require_auth
def update_profile(auth_key):
    """Update user profile - requires authentication"""
    customer = get_current_customer()

    # Verify the auth_key matches the authenticated customer
    if customer.auth_key != auth_key:
        return jsonify({
            'success': False,
            'message': 'Access denied',
            'error_code': 'ACCESS_DENIED'
        }), 403

    try:
        data = request.get_json() if request.is_json else request.form
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        address = data.get('address', '').strip()

        # Server-side validation
        if name and len(name) < 2:
            return jsonify({
                'success': False,
                'message': 'Name must be at least 2 characters long'
            }), 400

        # Email validation
        if email:
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_pattern, email):
                return jsonify({
                    'success': False,
                    'message': 'Please enter a valid email address'
                }), 400

        # Update customer fields
        if name:
            customer.name = sanitize_text(name)
        if email:
            customer.email = email
        if address:
            customer.address = address

        customer.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'customer': customer.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'error_code': 'SERVER_ERROR'
        }), 500

@main_bp.route('/customer/<auth_key>/info')
@require_auth
def get_customer_info(auth_key):
    """Get customer information by auth key - requires authentication"""
    customer = get_current_customer()

    # Verify the auth_key matches the authenticated customer
    if customer.auth_key != auth_key:
        return jsonify({
            'success': False,
            'message': 'Access denied',
            'error_code': 'ACCESS_DENIED'
        }), 403

    return jsonify({
        'success': True,
        'customer': customer.to_dict()
    }), 200

@main_bp.route('/api/pincode/<pincode>')
def get_pincode_info(pincode):
    """Get city and state information from PIN code"""
    try:
        # Validate PIN code format
        if not pincode.isdigit() or len(pincode) != 6:
            return jsonify({
                'success': False,
                'message': 'Invalid PIN code format'
            }), 400

        # Try multiple reliable API sources, starting with government data
        api_calls = [
            {
                'url': f'https://api.data.gov.in/catalog/709e9d78-bf11-487d-93fd-d547d24cc0ef?api-key=579b464db66ec23bdd0000015c26426692c446bb66a7696808147718&format=json&filters%5Bpincode%5D={pincode}',
                'type': 'gov_data'
            },
            {
                'url': f'https://api.postalpincode.in/pincode/{pincode}',
                'type': 'new_format'
            },
            {
                'url': f'http://www.postalpincode.in/api/pincode/{pincode}',
                'type': 'old_format'
            },
            {
                'url': f'https://api.zippopotam.us/IN/{pincode}',
                'type': 'zippopotam'
            }
        ]

        for api_call in api_calls:
            try:
                api_url = api_call['url']
                api_type = api_call['type']
                # Remove debug logs for faster execution
                response = requests.get(api_url, timeout=3)

                if response.status_code == 200:
                    data = response.json()

                    if api_type == 'gov_data':
                        # Government data.gov.in API format
                        if 'records' in data and len(data['records']) > 0:
                            location = data['records'][0]
                            return jsonify({
                                'success': True,
                                'city': location.get('district', ''),
                                'state': location.get('statename', ''),
                                'area': location.get('officename', ''),
                                'circle': location.get('circlename', ''),
                                'region': location.get('regionname', '')
                            }), 200

                    elif api_type == 'new_format':
                        # New postalpincode.in API format (array)
                        if isinstance(data, list) and len(data) > 0:
                            post_office_data = data[0]
                            if post_office_data.get('Status') == 'Success' and post_office_data.get('PostOffice'):
                                location = post_office_data['PostOffice'][0]
                                return jsonify({
                                    'success': True,
                                    'city': location.get('District', ''),
                                    'state': location.get('State', ''),
                                    'area': location.get('Name', '')
                                }), 200

                    elif api_type == 'old_format':
                        # Old postalpincode.in API format (object)
                        if data.get('Status') == 'Success' and data.get('PostOffice'):
                            location = data['PostOffice'][0]
                            return jsonify({
                                'success': True,
                                'city': location.get('District', ''),
                                'state': location.get('State', ''),
                                'area': location.get('Name', '')
                            }), 200

                    elif api_type == 'zippopotam':
                        # Zippopotam.us API format
                        if 'places' in data and len(data['places']) > 0:
                            location = data['places'][0]
                            return jsonify({
                                'success': True,
                                'city': location.get('place name', ''),
                                'state': location.get('state', ''),
                                'area': location.get('place name', '')
                            }), 200

            except requests.exceptions.RequestException:
                # Fail silently and try next API
                continue

        return jsonify({
            'success': False,
            'message': 'PIN code not found in any data source'
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Service temporarily unavailable'
        }), 500

@main_bp.context_processor
def utility_processor():
    """Add utility functions to template context"""
    def format_date(date_obj):
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.fromisoformat(date_obj).date()
            except:
                return date_obj
        return date_obj.strftime('%B %d, %Y') if date_obj else ''

    def format_time(time_obj):
        if isinstance(time_obj, str):
            try:
                time_obj = datetime.fromisoformat(time_obj).time()
            except:
                return time_obj
        return time_obj.strftime('%I:%M %p') if time_obj else ''

    def format_phone(phone):
        # Remove non-digits
        cleaned = ''.join(filter(str.isdigit, phone))
        if len(cleaned) == 10:
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
        return phone

    return dict(
        format_date=format_date,
        format_time=format_time,
        format_phone=format_phone,
        current_year=datetime.now().year
    )