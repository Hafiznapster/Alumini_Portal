from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        # Create all tables
        db.create_all()
        
        # Create an admin user
        admin = User(
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            name='Admin User',
            graduation_year=2023,
            role='admin'  # Set role instead of is_admin
        )
        db.session.add(admin)
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
