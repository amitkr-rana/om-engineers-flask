from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, date, time
from models import Customer, Service, Appointment, AppointmentType
from database import db

main_bp = Blueprint('main', __name__)

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


@main_bp.route('/dashboard')
def dashboard():
    """User dashboard after successful OTP login"""
    # Get phone number from URL parameter (primary) or session (fallback)
    customer_phone = request.args.get('phone', '').strip()
    if not customer_phone:
        customer_phone = session.get('customer_phone', '')

    customer_name = 'Guest'
    customer = None

    # Look up customer in database by phone number
    if customer_phone:
        try:
            customer = Customer.get_by_phone(customer_phone)
            if customer:
                customer_name = customer.name
        except Exception as e:
            pass

    # Final fallback to session data
    if not customer:
        customer_name = session.get('customer_name', 'Guest')

    return render_template('user_dashboard.html',
                         customer_name=customer_name,
                         customer_phone=customer_phone,
                         customer=customer)

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