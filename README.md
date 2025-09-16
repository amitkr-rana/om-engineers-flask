# Om Engineers - Home Repair Service Management App

A mobile-first Flask web application for managing home repair services and appointments. Built with responsive design principles and modern web development best practices.

## Features

### 🏠 Customer-Facing Features
- **Landing Page**: Clean, modern design matching the provided mockup
- **Service Booking**: Easy-to-use form for scheduling repair services
- **Quotation Requests**: Detailed form for requesting project estimates
- **Mobile-First Design**: Optimized for mobile devices with responsive layouts
- **Appointment Confirmation**: Clear confirmation pages with all details

### 🔧 Service Management
- **Service Catalog**: Comprehensive list of available services
- **Category Filtering**: Services organized by categories (Electrical, Plumbing, HVAC, etc.)
- **Search Functionality**: Find services by name or description
- **Service Details**: Complete information including duration and pricing

### 📅 Appointment Management
- **Dashboard**: Overview of all appointments with statistics
- **Status Tracking**: Pending, Confirmed, In Progress, Completed, Cancelled
- **Calendar View**: Visual calendar for appointment scheduling
- **Customer Management**: Integrated customer information storage
- **Appointment Updates**: Easy status updates and note management

### 📱 Mobile-First Design Principles
- **Progressive Enhancement**: Starts with mobile, enhances for desktop
- **Touch-Friendly**: 44px minimum touch targets
- **Responsive Typography**: rem/em units with 16px base
- **Flexible Layouts**: CSS Grid and Flexbox
- **Optimized Performance**: Minimal CSS/JS for fast loading

## Technology Stack

- **Backend**: Flask 2.3.3 (Python web framework)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with CSS Variables for design tokens
- **Data Storage**: In-memory Python data structures (ready for database integration)
- **Responsive Design**: Mobile-first CSS Grid and Flexbox

## Project Structure

```
om-engineers-flask/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── models/                     # Data models
│   ├── __init__.py
│   ├── customer.py            # Customer entity
│   ├── service.py             # Service entity
│   └── appointment.py         # Appointment entity
├── routes/                     # Route handlers
│   ├── __init__.py
│   ├── main.py               # Landing page and main routes
│   ├── appointments.py       # Appointment management
│   └── services.py           # Service catalog
├── static/                     # Static assets
│   ├── css/
│   │   └── main.css          # Main stylesheet with mobile-first design
│   ├── js/
│   │   └── app.js            # JavaScript functionality
│   └── images/
│       └── .gitkeep          # Placeholder for images
└── templates/                  # HTML templates
    ├── base.html              # Base template
    ├── index.html             # Landing page
    ├── get_started.html       # Service booking form
    ├── request_quotation.html # Quotation request form
    ├── appointment_confirmation.html # Confirmation page
    ├── contact.html           # Contact page
    ├── appointments/          # Appointment templates
    │   └── index.html        # Appointment dashboard
    └── services/              # Service templates
        └── index.html        # Service catalog
```

## Installation & Setup

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd om-engineers-flask
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## Usage

### Customer Workflow

1. **Visit Landing Page**: Navigate to the homepage to see services overview
2. **Book Service**: Click "Get Started" to schedule a repair service
3. **Request Quote**: Click "Request Quotation" for project estimates
4. **Confirmation**: Receive confirmation with appointment details

### Admin/Staff Workflow

1. **View Appointments**: Navigate to `/appointments` to see all bookings
2. **Manage Status**: Update appointment status (Confirm, Start, Complete, Cancel)
3. **Filter & Search**: Use filters to find specific appointments
4. **Customer Management**: View customer details and contact information

## API Endpoints

### Public Routes
- `GET /` - Landing page
- `GET /get-started` - Service booking form
- `POST /get-started` - Submit service booking
- `GET /request-quotation` - Quotation request form
- `POST /request-quotation` - Submit quotation request
- `GET /services` - Service catalog
- `GET /contact` - Contact information

### Management Routes
- `GET /appointments` - Appointment dashboard
- `GET /appointments/<id>` - Appointment details
- `POST /appointments/<id>/update` - Update appointment
- `GET /appointments/today` - Today's appointments
- `GET /appointments/upcoming` - Upcoming appointments

### API Routes (JSON)
- `GET /services/api/services` - Services data (JSON)
- `GET /appointments/api/appointments` - Appointments data (JSON)
- `GET /appointments/api/available-slots` - Available time slots (JSON)

## Configuration

### Environment Variables
Set these environment variables or modify `config.py`:

- `SECRET_KEY` - Flask secret key for sessions
- `CONTACT_PHONE` - Business phone number
- `CONTACT_EMAIL` - Business email address

### Default Services
The application comes with pre-configured services:
- Electrical Repair
- Plumbing Services
- AC Repair & Service
- Home Appliance Repair
- Carpentry Services
- Painting Services
- Cleaning Services
- Pest Control

## Mobile-First Design Features

### Responsive Breakpoints
- **Mobile**: < 576px (base styles)
- **Small Tablets**: ≥ 576px
- **Tablets**: ≥ 768px
- **Small Desktops**: ≥ 992px
- **Large Desktops**: ≥ 1200px

### Performance Optimizations
- Optimized CSS with minimal selectors
- Lazy loading for images
- Debounced search inputs
- Touch-friendly interactions
- Reduced bundle size

### Accessibility Features
- ARIA labels and roles
- Keyboard navigation support
- Screen reader announcements
- High contrast ratios
- Semantic HTML structure

## Data Models

### Customer
- ID, Name, Email, Phone, Address
- Created/Updated timestamps
- Search and filtering capabilities

### Service
- ID, Name, Description, Category, Duration, Price Range
- Icon representation
- Active/Inactive status

### Appointment
- ID, Customer ID, Service ID, Date/Time
- Status tracking (Pending → Confirmed → In Progress → Completed)
- Notes and address information
- Appointment type (Service/Quotation)

## Future Enhancements

### Database Integration
- PostgreSQL or MySQL database
- SQLAlchemy ORM integration
- Database migrations

### User Authentication
- Admin login system
- Role-based access control
- Customer portal

### Payment Integration
- Stripe or PayPal integration
- Online payment processing
- Invoice generation

### Notifications
- Email notifications
- SMS reminders
- Push notifications

### Advanced Features
- Technician assignment
- GPS tracking
- Photo uploads
- Service ratings and reviews

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/new-feature`)
6. Create a Pull Request

## License

This project is proprietary software for Om Engineers. All rights reserved.

## Support

For support and questions:
- Email: {{ config.CONTACT_EMAIL }}
- Phone: {{ config.CONTACT_PHONE }}
- Website: [Om Engineers](#)

---

Built with ❤️ for Om Engineers - Your Home, Our Expertise