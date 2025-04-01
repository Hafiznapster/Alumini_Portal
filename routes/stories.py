from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from models import Story
from extensions import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from forms.story import StoryForm

stories = Blueprint('stories', __name__, url_prefix='/stories')

@stories.route('/')
@login_required
def index():
    """View all published stories."""
    page = request.args.get('page', 1, type=int)
    stories = Story.query.filter_by(status='published').order_by(Story.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('stories/index.html', stories=stories)

@stories.route('/view/<int:story_id>')
@login_required
def view_story(story_id):
    """View a specific story."""
    story = Story.query.get_or_404(story_id)
    if story.status != 'published' and story.author_id != current_user.id:
        abort(403)
    
    # Increment view count
    story.views += 1
    db.session.commit()
    
    return render_template('stories/view.html', story=story)

@stories.route('/my-stories')
@login_required
def my_stories():
    """View stories written by the current user (alumni only)."""
    if current_user.role != 'alumni':
        flash('Only alumni can write stories.', 'warning')
        return redirect(url_for('stories.index'))
    
    stories = Story.query.filter_by(author_id=current_user.id).order_by(Story.created_at.desc()).all()
    return render_template('stories/my_stories.html', stories=stories)

@stories.route('/create', methods=['GET', 'POST'])
@login_required
def create_story():
    """Create a new story."""
    form = StoryForm()
    
    if form.validate_on_submit():
        # Handle image upload if present
        image_filename = None
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            # Ensure the upload directory exists
            upload_dir = os.path.join(current_app.static_folder, 'images', 'stories')
            os.makedirs(upload_dir, exist_ok=True)
            # Save the file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            image_filename = filename
        
        # Create new story
        story = Story(
            title=form.title.data,
            summary=form.summary.data,
            content=form.content.data,
            image=image_filename,
            author_id=current_user.id,
            status='draft'
        )
        
        db.session.add(story)
        db.session.commit()
        
        flash('Story created successfully!')
        return redirect(url_for('stories.view_story', story_id=story.id))
    
    return render_template('stories/create.html', form=form)

@stories.route('/edit/<int:story_id>', methods=['GET', 'POST'])
@login_required
def edit_story(story_id):
    """Edit an existing story."""
    story = Story.query.get_or_404(story_id)
    
    # Check if user is the author
    if story.author_id != current_user.id:
        abort(403)
    
    form = StoryForm(obj=story)
    
    if form.validate_on_submit():
        # Handle image upload if present
        if form.image.data:
            # Delete old image if it exists
            if story.image:
                old_image_path = os.path.join(current_app.static_folder, 'images', 'stories', story.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Save new image
            file = form.image.data
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.static_folder, 'images', 'stories')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            story.image = filename
        
        # Update story fields
        story.title = form.title.data
        story.summary = form.summary.data
        story.content = form.content.data
        
        db.session.commit()
        
        flash('Story updated successfully!')
        return redirect(url_for('stories.view_story', story_id=story.id))
    
    return render_template('stories/edit.html', form=form, story=story)

@stories.route('/delete/<int:story_id>')
@login_required
def delete_story(story_id):
    """Delete a story."""
    story = Story.query.get_or_404(story_id)
    
    # Check if user is the author
    if story.author_id != current_user.id:
        abort(403)
    
    # Delete story image if it exists
    if story.image:
        image_path = os.path.join(current_app.static_folder, 'images', 'stories', story.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(story)
    db.session.commit()
    
    flash('Story deleted successfully!')
    return redirect(url_for('stories.my_stories'))

@stories.route('/publish/<int:story_id>', methods=['POST'])
@login_required
def publish_story(story_id):
    """Publish a draft story."""
    story = Story.query.get_or_404(story_id)
    
    # Check if user is the author
    if story.author_id != current_user.id:
        abort(403)
    
    # Only allow publishing draft stories
    if story.status != 'draft':
        flash('Only draft stories can be published.', 'warning')
        return redirect(url_for('stories.view_story', story_id=story.id))
    
    story.status = 'published'
    db.session.commit()
    
    flash('Story published successfully!', 'success')
    return redirect(url_for('stories.view_story', story_id=story.id)) 