from flask import Flask, render_template, request, redirect, url_for, flash
import os

# Import extensions
from extensions import db, login_manager
from helpers import format_date, format_datetime, time_since  # Import the helper functions

def create_app():
    """Initialize the core application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register Jinja filters
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['time_since'] = time_since
    
    # Import models - this must be done after db is defined but before routes
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth as auth_blueprint
    from routes.profile import profile as profile_blueprint
    from routes.events import events as events_blueprint
    from routes.jobs import jobs as jobs_blueprint
    from routes.mentorship import mentorship as mentorship_blueprint
    from routes.forum import forum as forum_blueprint
    from routes.chat import chat as chat_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(events_blueprint)
    app.register_blueprint(jobs_blueprint)
    app.register_blueprint(mentorship_blueprint)
    app.register_blueprint(forum_blueprint)
    app.register_blueprint(chat_blueprint)
    
    @app.route('/')
    def index():
        """Render the homepage"""
        return render_template('index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
        
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True) 