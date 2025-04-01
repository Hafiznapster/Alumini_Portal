from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import extensions
from extensions import db, login_manager
from helpers import format_date, format_datetime, time_since  # Import the helper functions

def create_app():
    """Initialize the core application."""
    app = Flask(__name__)
    
    # Ensure the instance folder exists
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    try:
        os.makedirs(instance_path, exist_ok=True)
    except OSError as e:
        print(f"Error creating instance directory: {e}")
        
    # Configure database
    db_path = os.path.join(instance_path, 'database.db')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['UPLOAD_FOLDER'] = 'static/images'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register Jinja filters
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['time_since'] = time_since
    
    # Import all models - this must be done after db is defined but before routes
    from models import User, Event, EventRegistration, JobPost, JobApplication, Chat, ChatMessage, Mentor, MentorshipRelation, Story
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth as auth_bp
    from routes.profile import profile as profile_blueprint
    from routes.events import events as events_blueprint
    from routes.jobs import jobs as jobs_blueprint
    from routes.mentorship import bp as mentorship_bp
    from routes.stories import stories as stories_blueprint
    from routes.chat import chat as chat_blueprint
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(events_blueprint)
    app.register_blueprint(jobs_blueprint)
    app.register_blueprint(mentorship_bp)
    app.register_blueprint(stories_blueprint)
    app.register_blueprint(chat_blueprint)
    
    @app.route('/')
    def index():
        """Render the homepage"""
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        """About page."""
        return render_template('about.html')
    
    @app.route('/contact')
    def contact():
        """Contact page."""
        return render_template('contact.html')
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
        
    # Create database tables
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print(f"Database initialized at: {db_path}")
        except Exception as e:
            print(f"Error creating database: {e}")
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 