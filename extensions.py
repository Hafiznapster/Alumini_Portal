from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create extensions but don't initialize them yet
db = SQLAlchemy()
login_manager = LoginManager()

