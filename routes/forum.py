from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import ForumCategory, ForumPost, ForumComment
from datetime import datetime

forum = Blueprint('forum', __name__, url_prefix='/forum')

@forum.route('/')
@login_required
def index():
    """View forum categories."""
    categories = ForumCategory.query.all()
    return render_template('forum/index.html', categories=categories)

@forum.route('/category/<int:category_id>')
def view_category(category_id):
    """View posts in a specific category."""
    category = ForumCategory.query.get_or_404(category_id)
    posts = ForumPost.query.filter_by(category_id=category_id).order_by(ForumPost.created_at.desc()).all()
    return render_template('forum/category.html', category=category, posts=posts)

@forum.route('/post/<int:post_id>')
def view_post(post_id):
    """View a specific forum post and its comments."""
    post = ForumPost.query.get_or_404(post_id)
    comments = post.comments
    return render_template('forum/post.html', post=post, comments=comments)

@forum.route('/create-post/<int:category_id>', methods=['GET', 'POST'])
@login_required
def create_post(category_id):
    """Create a new forum post."""
    category = ForumCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        from app import db
        title = request.form.get('title')
        content = request.form.get('content')
        
        new_post = ForumPost(
            title=title,
            content=content,
            user_id=current_user.id,
            category_id=category_id
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('Your post has been created!')
        return redirect(url_for('forum.view_post', post_id=new_post.id))
        
    return render_template('forum/create_post.html', category=category)

@forum.route('/add-comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a comment to a forum post."""
    post = ForumPost.query.get_or_404(post_id)
    content = request.form.get('content')
    
    if not content:
        flash('Comment cannot be empty.')
        return redirect(url_for('forum.view_post', post_id=post_id))
        
    from app import db
    new_comment = ForumComment(
        content=content,
        user_id=current_user.id,
        post_id=post_id
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    flash('Your comment has been added!')
    return redirect(url_for('forum.view_post', post_id=post_id))

@forum.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit a forum post."""
    post = ForumPost.query.get_or_404(post_id)
    
    # Check if user is the author or an admin
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this post.')
        return redirect(url_for('forum.view_post', post_id=post_id))
        
    if request.method == 'POST':
        from app import db
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        
        db.session.commit()
        
        flash('Your post has been updated!')
        return redirect(url_for('forum.view_post', post_id=post_id))
        
    return render_template('forum/edit_post.html', post=post)

@forum.route('/delete-post/<int:post_id>')
@login_required
def delete_post(post_id):
    """Delete a forum post."""
    post = ForumPost.query.get_or_404(post_id)
    
    # Check if user is the author or an admin
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this post.')
        return redirect(url_for('forum.view_post', post_id=post_id))
        
    from app import db
    # Delete all comments first
    for comment in post.comments:
        db.session.delete(comment)
        
    db.session.delete(post)
    db.session.commit()
    
    flash('Your post has been deleted!')
    return redirect(url_for('forum.view_category', category_id=post.category_id))