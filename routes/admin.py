from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, time
from models import Customer, Service, Appointment, AppointmentStatus, AppointmentType
from database import db
import traceback

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def index():
    """Admin dashboard with table statistics"""
    try:
        # Get counts for all tables
        customer_count = Customer.query.count()
        service_count = Service.query.count()
        appointment_count = Appointment.query.count()

        # Get recent records
        recent_customers = Customer.query.order_by(Customer.created_at.desc()).limit(5).all()
        recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()

        stats = {
            'customers': customer_count,
            'services': service_count,
            'appointments': appointment_count
        }

        return render_template('admin/index.html',
                             stats=stats,
                             recent_customers=recent_customers,
                             recent_appointments=recent_appointments)
    except Exception as e:
        flash(f'Error loading admin dashboard: {str(e)}', 'error')
        return render_template('admin/index.html', stats={}, recent_customers=[], recent_appointments=[])

# Customer CRUD
@admin_bp.route('/customers')
def customers():
    """List all customers"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    query = Customer.query
    if search:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%'),
                Customer.phone.ilike(f'%{search}%')
            )
        )

    customers = query.order_by(Customer.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('admin/customers.html', customers=customers, search=search)

@admin_bp.route('/customers/new')
def new_customer():
    """New customer form"""
    return render_template('admin/customer_form.html', customer=None)

@admin_bp.route('/customers/create', methods=['POST'])
def create_customer():
    """Create new customer"""
    try:
        customer = Customer(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form.get('address', '')
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer created successfully!', 'success')
        return redirect(url_for('admin.customers'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating customer: {str(e)}', 'error')
        return redirect(url_for('admin.new_customer'))

@admin_bp.route('/customers/<int:customer_id>/edit')
def edit_customer(customer_id):
    """Edit customer form"""
    customer = Customer.query.get_or_404(customer_id)
    return render_template('admin/customer_form.html', customer=customer)

@admin_bp.route('/customers/<int:customer_id>/update', methods=['POST'])
def update_customer(customer_id):
    """Update customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        customer.name = request.form['name']
        customer.email = request.form['email']
        customer.phone = request.form['phone']
        customer.address = request.form.get('address', '')
        customer.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('admin.customers'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating customer: {str(e)}', 'error')
        return redirect(url_for('admin.edit_customer', customer_id=customer_id))

@admin_bp.route('/customers/<int:customer_id>/delete', methods=['POST'])
def delete_customer(customer_id):
    """Delete customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting customer: {str(e)}', 'error')
    return redirect(url_for('admin.customers'))

# Service CRUD
@admin_bp.route('/services')
def services():
    """List all services"""
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)

    query = Service.query
    if search:
        query = query.filter(
            db.or_(
                Service.name.ilike(f'%{search}%'),
                Service.description.ilike(f'%{search}%')
            )
        )
    if category:
        query = query.filter(Service.category == category)

    services = query.order_by(Service.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    categories = Service.get_categories(active_only=False)

    return render_template('admin/services.html',
                         services=services,
                         search=search,
                         categories=categories,
                         current_category=category)

@admin_bp.route('/services/new')
def new_service():
    """New service form"""
    return render_template('admin/service_form.html', service=None)

@admin_bp.route('/services/create', methods=['POST'])
def create_service():
    """Create new service"""
    try:
        service = Service(
            name=request.form['name'],
            description=request.form['description'],
            category=request.form['category'],
            duration=request.form['duration'],
            price_range=request.form['price_range'],
            icon=request.form.get('icon', '🔧'),
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(service)
        db.session.commit()
        flash('Service created successfully!', 'success')
        return redirect(url_for('admin.services'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating service: {str(e)}', 'error')
        return redirect(url_for('admin.new_service'))

@admin_bp.route('/services/<int:service_id>/edit')
def edit_service(service_id):
    """Edit service form"""
    service = Service.query.get_or_404(service_id)
    return render_template('admin/service_form.html', service=service)

@admin_bp.route('/services/<int:service_id>/update', methods=['POST'])
def update_service(service_id):
    """Update service"""
    try:
        service = Service.query.get_or_404(service_id)
        service.name = request.form['name']
        service.description = request.form['description']
        service.category = request.form['category']
        service.duration = request.form['duration']
        service.price_range = request.form['price_range']
        service.icon = request.form.get('icon', '🔧')
        service.is_active = request.form.get('is_active') == 'on'
        service.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('admin.services'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating service: {str(e)}', 'error')
        return redirect(url_for('admin.edit_service', service_id=service_id))

@admin_bp.route('/services/<int:service_id>/delete', methods=['POST'])
def delete_service(service_id):
    """Delete service"""
    try:
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting service: {str(e)}', 'error')
    return redirect(url_for('admin.services'))

# Appointment CRUD
@admin_bp.route('/appointments')
def appointments():
    """List all appointments"""
    status = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    page = request.args.get('page', 1, type=int)

    query = Appointment.query
    if status:
        try:
            status_enum = AppointmentStatus(status)
            query = query.filter(Appointment.status == status_enum)
        except ValueError:
            pass

    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Appointment.appointment_date == filter_date)
        except ValueError:
            pass

    appointments = query.order_by(Appointment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    # Add customer and service info
    appointment_details = []
    for apt in appointments.items:
        customer = Customer.query.get(apt.customer_id)
        service = Service.query.get(apt.service_id)
        appointment_details.append({
            'appointment': apt,
            'customer': customer,
            'service': service
        })

    return render_template('admin/appointments.html',
                         appointments=appointments,
                         appointment_details=appointment_details,
                         statuses=list(AppointmentStatus),
                         current_status=status,
                         current_date=date_filter)

@admin_bp.route('/appointments/new')
def new_appointment():
    """New appointment form"""
    customers = Customer.query.all()
    services = Service.query.filter_by(is_active=True).all()
    return render_template('admin/appointment_form.html',
                         appointment=None,
                         customers=customers,
                         services=services)

@admin_bp.route('/appointments/create', methods=['POST'])
def create_appointment():
    """Create new appointment"""
    try:
        appointment = Appointment(
            customer_id=int(request.form['customer_id']),
            service_id=int(request.form['service_id']),
            appointment_date=datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(request.form['appointment_time'], '%H:%M').time(),
            appointment_type=AppointmentType(request.form['appointment_type']),
            status=AppointmentStatus(request.form['status']),
            notes=request.form.get('notes', ''),
            address=request.form.get('address', '')
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment created successfully!', 'success')
        return redirect(url_for('admin.appointments'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating appointment: {str(e)}', 'error')
        return redirect(url_for('admin.new_appointment'))

@admin_bp.route('/appointments/<int:appointment_id>/edit')
def edit_appointment(appointment_id):
    """Edit appointment form"""
    appointment = Appointment.query.get_or_404(appointment_id)
    customers = Customer.query.all()
    services = Service.query.filter_by(is_active=True).all()
    return render_template('admin/appointment_form.html',
                         appointment=appointment,
                         customers=customers,
                         services=services)

@admin_bp.route('/appointments/<int:appointment_id>/update', methods=['POST'])
def update_appointment(appointment_id):
    """Update appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.customer_id = int(request.form['customer_id'])
        appointment.service_id = int(request.form['service_id'])
        appointment.appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()
        appointment.appointment_time = datetime.strptime(request.form['appointment_time'], '%H:%M').time()
        appointment.appointment_type = AppointmentType(request.form['appointment_type'])
        appointment.status = AppointmentStatus(request.form['status'])
        appointment.notes = request.form.get('notes', '')
        appointment.address = request.form.get('address', '')
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('admin.appointments'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating appointment: {str(e)}', 'error')
        return redirect(url_for('admin.edit_appointment', appointment_id=appointment_id))

@admin_bp.route('/appointments/<int:appointment_id>/delete', methods=['POST'])
def delete_appointment(appointment_id):
    """Delete appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting appointment: {str(e)}', 'error')
    return redirect(url_for('admin.appointments'))

# Database utilities
@admin_bp.route('/database/reset', methods=['POST'])
def reset_database():
    """Reset database (development only)"""
    try:
        from database import reset_database
        reset_database()
        flash('Database reset successfully!', 'success')
    except Exception as e:
        flash(f'Error resetting database: {str(e)}', 'error')
    return redirect(url_for('admin.index'))

@admin_bp.route('/api/stats')
def api_stats():
    """API endpoint for database statistics"""
    try:
        stats = {
            'customers': Customer.query.count(),
            'services': Service.query.count(),
            'appointments': Appointment.query.count(),
            'active_services': Service.query.filter_by(is_active=True).count(),
            'pending_appointments': Appointment.query.filter_by(status=AppointmentStatus.PENDING).count(),
            'completed_appointments': Appointment.query.filter_by(status=AppointmentStatus.COMPLETED).count()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500