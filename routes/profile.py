from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from models import User
from PIL import Image

profile = Blueprint('profile', __name__, url_prefix='/profile')

def allowed_file(filename):
    """Check if the file extension is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_image(file, user_id):
    """Save and process the profile image."""
    if file and allowed_file(file.filename):
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate secure filename
        filename = secure_filename(f"{user_id}_{file.filename}")
        filepath = os.path.join(upload_dir, filename)
        
        # Open and process image with Pillow
        img = Image.open(file)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize image to 300x300 while maintaining aspect ratio
        img.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        # Save the processed image
        img.save(filepath, quality=85, optimize=True)
        
        return f"uploads/profile_pics/{filename}"
    return None

@profile.route('/')
@login_required
def view_profile():
    """View user's profile."""
    return render_template('profile/view.html', user=current_user)

@profile.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user's profile."""
    if request.method == 'POST':
        from app import db
        name = request.form.get('name')
        bio = request.form.get('bio')
        graduation_year = request.form.get('graduation_year')
        degree = request.form.get('degree')
        major = request.form.get('major')

        current_user.name = name
        current_user.bio = bio
        current_user.graduation_year = graduation_year
        current_user.degree = degree
        current_user.major = major

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                profile_pic_path = save_profile_image(file, current_user.id)
                if profile_pic_path:
                    current_user.profile_pic = profile_pic_path

        db.session.commit()
        flash('Your profile has been updated!')
        return redirect(url_for('profile.view_profile'))

    return render_template('profile/edit.html', user=current_user)

@profile.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user's password."""
    if request.method == 'POST':
        from app import db
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check if current password is correct
        if not check_password_hash(current_user.password, old_password):
            flash('Current password is incorrect.')
            return redirect(url_for('profile.change_password'))

        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.')
            return redirect(url_for('profile.change_password'))

        # Update password
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()

        flash('Your password has been updated!')
        return redirect(url_for('profile.view_profile'))

    return render_template('profile/change_password.html')

@profile.route('/alumni-directory')
@login_required
def alumni_directory():
    """View directory of all alumni."""
    alumni = User.query.order_by(User.graduation_year.desc()).all()
    return render_template('profile/directory.html', alumni=alumni)

@profile.route('/view/<int:user_id>')
@login_required
def view_user(user_id):
    """View another user's profile."""
    user = User.query.get_or_404(user_id)
    return render_template('profile/view_user.html', user=user)