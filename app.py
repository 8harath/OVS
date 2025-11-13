# app.py - Main Application File
import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
from models import db, Voter
from utils import mail, create_sample_data, logger
from datetime import datetime

# Import blueprints
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.admin import admin_bp
from blueprints.api import api_bp

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return Voter.query.get(int(user_id))

    # Setup Flask-Limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )

    # Apply rate limiting to auth routes
    limiter.limit("5 per minute")(auth_bp)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Create database tables and sample data
    with app.app_context():
        db.create_all()
        create_sample_data(db)
        logger.info("Database initialized successfully")

    # Template context processors
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    @app.context_processor
    def inject_config():
        return {'config': app.config}

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error(f'Internal server error: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return render_template('errors/429.html'), 429

    # Shell context for flask shell
    @app.shell_context_processor
    def make_shell_context():
        from models import Voter, Candidate, Vote, Election, Announcement
        return {
            'db': db,
            'Voter': Voter,
            'Candidate': Candidate,
            'Vote': Vote,
            'Election': Election,
            'Announcement': Announcement
        }

    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'candidates'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'id_documents'), exist_ok=True)

    logger.info(f"Application started in {config_name} mode")

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Only run with debug mode from environment variable
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )