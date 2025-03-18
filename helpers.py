import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions=None):
    """Check if the file extension is allowed."""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, folder='uploads'):
    """Save a file to the specified folder and return the filename."""
    if file and allowed_file(file.filename):
        # Generate a unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Ensure the upload folder exists
        upload_folder = os.path.join(current_app.static_folder, folder)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Save the file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

def format_date(date):
    """Format a datetime object for display."""
    if isinstance(date, datetime):
        return date.strftime('%B %d, %Y')
    return date

def format_datetime(date):
    """Format a datetime object with time for display."""
    if isinstance(date, datetime):
        return date.strftime('%B %d, %Y at %I:%M %p')
    return date

def time_since(date):
    """Return a string representing time since the given datetime."""
    now = datetime.utcnow()
    diff = now - date
    
    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days
    
    if days > 30:
        months = days // 30
        if months > 12:
            years = months // 12
            return f"{int(years)} year{'s' if years != 1 else ''} ago"
        return f"{int(months)} month{'s' if months != 1 else ''} ago"
    if days > 0:
        return f"{int(days)} day{'s' if days != 1 else ''} ago"
    if hours > 0:
        return f"{int(hours)} hour{'s' if hours != 1 else ''} ago"
    if minutes > 0:
        return f"{int(minutes)} minute{'s' if minutes != 1 else ''} ago"
    return "just now"

def validate_password(password):
    """Validate password strength."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one number.")
    if not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter.")
    if not any(char in "!@#$%^&*()_-+={}[]|:;<>,.?/~`" for char in password):
        errors.append("Password must contain at least one special character.")
        
    return errors

def get_graduation_years(start_year=1950, end_year=None):
    """Get a list of graduation years for dropdowns."""
    if end_year is None:
        end_year = datetime.utcnow().year + 5
        
    return list(range(end_year, start_year - 1, -1))

def truncate_text(text, max_length=100):
    """Truncate text to a maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...' 