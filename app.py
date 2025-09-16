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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)