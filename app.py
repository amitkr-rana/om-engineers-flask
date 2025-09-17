from flask import Flask
from config import Config
from database import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import all models first to ensure proper registration
    import models

    # Initialize database
    init_db(app)

    # Register blueprints
    from routes.main import main_bp
    from routes.appointments import appointments_bp
    from routes.services import services_bp
    from routes.admin import admin_bp
    from routes.otp import otp_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(services_bp, url_prefix='/services')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(otp_bp, url_prefix='/api/otp')

    # Add headers for API compatibility
    @app.after_request
    def after_request(response):
        # Allow iframe embedding (remove X-Frame-Options or set to SAMEORIGIN)
        response.headers.pop('X-Frame-Options', None)

        # Set CORS headers for API access
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Auth-Token, X-Auth-Key, X-Requested-With'
        response.headers['Access-Control-Allow-Credentials'] = 'false'  # Not needed for token-based auth

        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)