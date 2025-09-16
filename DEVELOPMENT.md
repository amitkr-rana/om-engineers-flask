# Development Guide

## Quick Start

1. **Start the development server:**
   ```bash
   python app.py
   ```

2. **Visit the application:**
   - Homepage: http://localhost:5000
   - Services: http://localhost:5000/services
   - Appointments: http://localhost:5000/appointments
   - Contact: http://localhost:5000/contact

## Development Features

### Auto-reload
The Flask app runs in debug mode, so changes to Python files will automatically restart the server.

### Mobile Testing
Test the responsive design using browser developer tools:
1. Open browser developer tools (F12)
2. Click the device toggle button
3. Select different device sizes to test responsiveness

### Add Hero Image
To add the hero image shown in the design:
1. Save your hero image as `static/images/hero-interior.jpg`
2. The image should be approximately 800x600px for best results
3. The page will automatically load the image once it's in place

## Key URLs for Testing

### Customer Flows
- **Landing Page**: `/`
- **Book Service**: `/get-started`
- **Request Quote**: `/request-quotation`
- **Services Catalog**: `/services`

### Admin/Management
- **All Appointments**: `/appointments`
- **Today's Appointments**: `/appointments/today`
- **Upcoming Appointments**: `/appointments/upcoming`

### API Endpoints (JSON)
- **Services API**: `/services/api/services`
- **Appointments API**: `/appointments/api/appointments`
- **Available Slots**: `/appointments/api/available-slots?date=2024-12-25`

## Testing the Application

### 1. Test Service Booking
1. Go to `/get-started`
2. Fill out the form with test data
3. Submit and verify confirmation page
4. Check `/appointments` to see the new appointment

### 2. Test Quotation Request
1. Go to `/request-quotation`
2. Fill out the quotation form
3. Submit and verify confirmation
4. Check appointments list for the quotation request

### 3. Test Appointment Management
1. Go to `/appointments`
2. Click on an appointment to view details
3. Test status updates (Confirm, Start, Complete)
4. Test filtering and search functionality

### 4. Test Mobile Responsiveness
1. Use browser dev tools to simulate different screen sizes
2. Verify touch-friendly button sizes (minimum 44px)
3. Test form usability on mobile devices
4. Verify navigation menu works on mobile

## Customization

### Branding
- Update `config.py` for contact information
- Modify CSS variables in `static/css/main.css` for colors
- Replace service icons and descriptions in `models/service.py`

### Services
- Add new services in `Service.initialize_default_services()`
- Modify service categories and pricing
- Update service icons (emojis)

### Styling
- All design tokens are in CSS variables at the top of `main.css`
- Mobile-first approach: start with mobile styles, add desktop media queries
- Follow the established pattern for new components

## Production Deployment

### Environment Setup
```bash
# Set production environment variables
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
export CONTACT_PHONE=+91-XXXX-XXXX
export CONTACT_EMAIL=info@omengineers.com
```

### Database Migration
When ready to add a database:
1. Install database dependencies (SQLAlchemy, PostgreSQL/MySQL drivers)
2. Replace in-memory storage with database models
3. Add database initialization and migration scripts
4. Update configuration for database URL

### Production Server
Replace the development server with a production WSGI server:
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

## Troubleshooting

### Common Issues
1. **Port already in use**: Kill existing Flask processes or use a different port
2. **CSS not updating**: Hard refresh (Ctrl+F5) or clear browser cache
3. **Import errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
4. **Template not found**: Check file paths and template directory structure

### Debug Mode
The app runs in debug mode by default, providing:
- Detailed error pages
- Auto-reload on file changes
- Interactive debugger in browser

### Performance Testing
Test mobile performance:
1. Use browser Network tab to check load times
2. Test on actual mobile devices when possible
3. Verify touch interactions work smoothly
4. Check for any JavaScript errors in console