from flask import Blueprint, render_template, request, jsonify
from models import Service

services_bp = Blueprint('services', __name__)

@services_bp.route('/')
def index():
    """Services listing page"""
    # Get filter parameters
    category = request.args.get('category', '')
    search = request.args.get('search', '')

    # Get all services
    services = Service.get_all()

    # Filter by category if specified
    if category:
        services = [s for s in services if s.category.lower() == category.lower()]

    # Filter by search query if specified
    if search:
        search_results = Service.search(search)
        services = [s for s in services if s in search_results]

    # Get all categories for filter
    categories = Service.get_categories()

    return render_template('services/index.html',
                         services=services,
                         categories=categories,
                         current_category=category,
                         current_search=search)

@services_bp.route('/<int:service_id>')
def detail(service_id):
    """Service detail page"""
    service = Service.query.get(service_id)
    if not service:
        return render_template('404.html'), 404

    # Get related services (same category)
    related_services = Service.get_by_category(service.category)
    related_services = [s for s in related_services if s.id != service_id][:3]

    return render_template('services/detail.html',
                         service=service,
                         related_services=related_services)

@services_bp.route('/api/services')
def api_services():
    """API endpoint for services (JSON)"""
    # Get filter parameters
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    active_only = request.args.get('active_only', 'true').lower() == 'true'

    # Get services
    services = Service.get_all(active_only=active_only)

    # Filter by category if specified
    if category:
        services = [s for s in services if s.category.lower() == category.lower()]

    # Filter by search query if specified
    if search:
        search_results = Service.search(search, active_only=active_only)
        services = [s for s in services if s in search_results]

    # Convert to dict format
    services_data = [service.to_dict() for service in services]

    return jsonify({
        'services': services_data,
        'total': len(services_data),
        'categories': Service.get_categories(active_only=active_only)
    })

@services_bp.route('/api/services/<int:service_id>')
def api_service_detail(service_id):
    """API endpoint for single service (JSON)"""
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'error': 'Service not found'}), 404

    return jsonify(service.to_dict())

@services_bp.route('/categories')
def categories():
    """Service categories page"""
    categories = Service.get_categories()
    category_data = []

    for category in categories:
        services = Service.get_by_category(category)
        category_data.append({
            'name': category,
            'count': len(services),
            'services': services[:3]  # Show first 3 services as preview
        })

    return render_template('services/categories.html', categories=category_data)