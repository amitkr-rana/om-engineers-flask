from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, time, timedelta
from models import Appointment, AppointmentStatus, AppointmentType, Customer, Service
from database import db

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/')
def index():
    """Appointments listing page"""
    # Get filter parameters
    status_filter = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    customer_search = request.args.get('customer', '')

    # Get all appointments
    appointments = Appointment.query.all()

    # Filter by status if specified
    if status_filter:
        try:
            status_enum = AppointmentStatus(status_filter)
            appointments = [apt for apt in appointments if apt.status == status_enum]
        except ValueError:
            pass

    # Filter by date if specified
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = [apt for apt in appointments if apt.appointment_date == filter_date]
        except ValueError:
            pass

    # Filter by customer if specified
    if customer_search:
        customer_search = customer_search.lower()
        filtered_appointments = []
        for apt in appointments:
            customer = Customer.query.get(apt.customer_id)
            if customer and (customer_search in customer.name.lower() or
                           customer_search in customer.email.lower() or
                           customer_search in customer.phone):
                filtered_appointments.append(apt)
        appointments = filtered_appointments

    # Sort by appointment date and time
    appointments.sort(key=lambda x: (x.appointment_date, x.appointment_time), reverse=True)

    # Add customer and service info to appointments
    appointment_details = []
    for apt in appointments:
        customer = Customer.query.get(apt.customer_id)
        service = Service.query.get(apt.service_id)
        appointment_details.append({
            'appointment': apt,
            'customer': customer,
            'service': service
        })

    # Get statistics
    stats = Appointment.get_statistics()

    return render_template('appointments/index.html',
                         appointment_details=appointment_details,
                         stats=stats,
                         current_status=status_filter,
                         current_date=date_filter,
                         current_customer=customer_search,
                         statuses=list(AppointmentStatus))

@appointments_bp.route('/<int:appointment_id>')
def detail(appointment_id):
    """Appointment detail page"""
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        flash('Appointment not found', 'error')
        return redirect(url_for('appointments.index'))

    customer = Customer.query.get(appointment.customer_id)
    service = Service.query.get(appointment.service_id)

    # Get available time slots for rescheduling (next 30 days)
    available_dates = []
    for i in range(1, 31):  # Next 30 days
        check_date = date.today() + timedelta(days=i)
        available_slots = Appointment.get_available_time_slots(check_date)
        if available_slots:
            available_dates.append({
                'date': check_date,
                'slots': available_slots[:5]  # Limit to 5 slots per day
            })

    return render_template('appointments/detail.html',
                         appointment=appointment,
                         customer=customer,
                         service=service,
                         available_dates=available_dates,
                         statuses=list(AppointmentStatus))

@appointments_bp.route('/<int:appointment_id>/update', methods=['POST'])
def update(appointment_id):
    """Update appointment"""
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        flash('Appointment not found', 'error')
        return redirect(url_for('appointments.index'))

    action = request.form.get('action')

    try:
        if action == 'confirm':
            appointment.confirm()
            flash('Appointment confirmed successfully', 'success')

        elif action == 'start':
            appointment.start_service()
            flash('Service started', 'success')

        elif action == 'complete':
            actual_cost = request.form.get('actual_cost', '')
            technician_notes = request.form.get('technician_notes', '')
            appointment.complete(actual_cost=actual_cost, technician_notes=technician_notes)
            flash('Appointment completed successfully', 'success')

        elif action == 'cancel':
            reason = request.form.get('reason', '')
            appointment.cancel(reason=reason)
            flash('Appointment cancelled', 'warning')

        elif action == 'reschedule':
            new_date = request.form.get('new_date')
            new_time = request.form.get('new_time')
            reason = request.form.get('reason', '')

            if new_date and new_time:
                try:
                    parsed_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                    parsed_time = datetime.strptime(new_time, '%H:%M').time()

                    if parsed_date < date.today():
                        flash('New appointment date must be in the future', 'error')
                    else:
                        appointment.reschedule(parsed_date, parsed_time, reason)
                        flash('Appointment rescheduled successfully', 'success')
                except ValueError:
                    flash('Invalid date or time format', 'error')
            else:
                flash('Please provide new date and time', 'error')

        elif action == 'update_notes':
            notes = request.form.get('notes', '')
            estimated_cost = request.form.get('estimated_cost', '')
            estimated_duration = request.form.get('estimated_duration', '')

            appointment.update(
                notes=notes,
                estimated_cost=estimated_cost,
                estimated_duration=estimated_duration
            )
            flash('Appointment updated successfully', 'success')

        else:
            flash('Invalid action', 'error')

    except Exception as e:
        flash('An error occurred while updating the appointment', 'error')

    return redirect(url_for('appointments.detail', appointment_id=appointment_id))

@appointments_bp.route('/today')
def today():
    """Today's appointments"""
    today_appointments = Appointment.get_today()

    # Add customer and service info
    appointment_details = []
    for apt in today_appointments:
        customer = Customer.query.get(apt.customer_id)
        service = Service.query.get(apt.service_id)
        appointment_details.append({
            'appointment': apt,
            'customer': customer,
            'service': service
        })

    # Sort by time
    appointment_details.sort(key=lambda x: x['appointment'].appointment_time)

    return render_template('appointments/today.html', appointment_details=appointment_details)

@appointments_bp.route('/upcoming')
def upcoming():
    """Upcoming appointments (next 7 days)"""
    upcoming_appointments = Appointment.get_upcoming(days=7)

    # Add customer and service info
    appointment_details = []
    for apt in upcoming_appointments:
        customer = Customer.query.get(apt.customer_id)
        service = Service.query.get(apt.service_id)
        appointment_details.append({
            'appointment': apt,
            'customer': customer,
            'service': service
        })

    # Sort by date and time
    appointment_details.sort(key=lambda x: (x['appointment'].appointment_date, x['appointment'].appointment_time))

    return render_template('appointments/upcoming.html', appointment_details=appointment_details)

@appointments_bp.route('/calendar')
def calendar():
    """Calendar view of appointments"""
    # Get date range (current month)
    today = date.today()
    start_date = date(today.year, today.month, 1)

    # Calculate end date (last day of month)
    if today.month == 12:
        end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

    # Get appointments for the month
    appointments = Appointment.get_by_date_range(start_date, end_date)

    # Group appointments by date
    appointments_by_date = {}
    for apt in appointments:
        date_key = apt.appointment_date.isoformat()
        if date_key not in appointments_by_date:
            appointments_by_date[date_key] = []

        customer = Customer.query.get(apt.customer_id)
        service = Service.query.get(apt.service_id)

        appointments_by_date[date_key].append({
            'appointment': apt,
            'customer': customer,
            'service': service
        })

    return render_template('appointments/calendar.html',
                         appointments_by_date=appointments_by_date,
                         current_month=today,
                         start_date=start_date,
                         end_date=end_date)

@appointments_bp.route('/api/appointments')
def api_appointments():
    """API endpoint for appointments (JSON)"""
    # Get filter parameters
    status_filter = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # Get appointments
    appointments = Appointment.get_all()

    # Apply filters
    if status_filter:
        try:
            status_enum = AppointmentStatus(status_filter)
            appointments = [apt for apt in appointments if apt.status == status_enum]
        except ValueError:
            pass

    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = [apt for apt in appointments if apt.appointment_date == filter_date]
        except ValueError:
            pass

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            appointments = Appointment.get_by_date_range(start, end)
        except ValueError:
            pass

    # Convert to dict format with customer and service info
    appointments_data = []
    for apt in appointments:
        customer = Customer.query.get(apt.customer_id)
        service = Service.query.get(apt.service_id)

        apt_data = apt.to_dict()
        apt_data['customer'] = customer.to_dict() if customer else None
        apt_data['service'] = service.to_dict() if service else None

        appointments_data.append(apt_data)

    return jsonify({
        'appointments': appointments_data,
        'total': len(appointments_data),
        'statistics': Appointment.get_statistics()
    })

@appointments_bp.route('/api/available-slots')
def api_available_slots():
    """API endpoint for available time slots"""
    date_str = request.args.get('date')
    duration = int(request.args.get('duration', 2))  # Default 2 hours

    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    if target_date < date.today():
        return jsonify({'error': 'Date must be in the future'}), 400

    available_slots = Appointment.get_available_time_slots(target_date, duration)
    slots_data = [slot.strftime('%H:%M') for slot in available_slots]

    return jsonify({
        'date': date_str,
        'available_slots': slots_data,
        'total_slots': len(slots_data)
    })